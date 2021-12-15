# %%
# Prepare
import visvalingamwyatt as vw
import json
import numpy as np
import copy
import plotly.express as px
from shapely.geometry import Polygon
from PIL import Image, ImageDraw
import statistics
from sys import getsizeof
import requests
from io import BytesIO
import plotly.graph_objects as go

def simplify_polygon(polygon, ratio = 0.5, min_points = 4):
    #VW algorithm used
    simplifier = vw.Simplifier(polygon)
    number = max( min_points , int(pow(len(polygon), ratio)))  
    simple_poly = simplifier.simplify( number=number)
    return simple_poly

def visualize_line_plotly(x,y,title="X vs Y", xLabel = "polygon subsampling ratio", yLabel = 'Remaining Labels'):
    fig = px.line(x=x,y=y, title=title )
    fig.update_layout(xaxis_title_text=xLabel, yaxis_title_text=yLabel)
    fig.show()

def visualize_scatter_plotly(x,y,title="X vs Y", xLabel = "polygon subsampling ratio", yLabel = 'Remaining Labels'):
    fig = px.scatter(x=x,y=y, title=title )
    fig.update_layout(xaxis_title_text=xLabel, yaxis_title_text=yLabel)
    fig.show()

def visualize_stats_by_class(d,values,metric='iou',title="IOUs of Objects by Class",xLabel="Class Name",yLabel="Average IOU"):
    fig = go.Figure()
    for value in values:
        sub_dict = d[value]
        x = list(sub_dict.keys())
        y = [sub_dict[el][metric] for el in sub_dict.keys()]
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            name=str(value),
            #marker_color='indianred'
        ))
    fig.update_layout(barmode='group', xaxis_tickangle=-45, legend_title = "Simplification Ratios", title_text=title, xaxis_title_text=xLabel, yaxis_title_text=yLabel)
    fig.show()


def calculate_iou(old_poly, new_poly):
    p1 = Polygon(old_poly)
    p2 = Polygon(new_poly)
    if ((not p1.is_valid) or (not p2.is_valid)):
        return 0 
    intersect = p1.intersection(p2).area
    union = p1.union(p2).area
    iou = intersect / union
    return iou

def polygon_on_image(polygon, im, show=True, save_title=""):
    new_poly = []
    for point in polygon:
        new_poly.append( (point[0], point[1]) )
    #image = Image.new("RGB", (im.shape[1], im.shape[0]))
    draw = ImageDraw.Draw(im, 'RGBA')
    draw.polygon((new_poly), (255, 0, 0, 125))
    if save_title:
        im.save(save_title)
    if show:
        im.show()
    return im

def fetch_benchmark_assets(benchmark_assets, data_origin):
    images = {}
    for key in benchmark_assets:
        url = data_origin[key]['asset']
        response = requests.get(url)
        images[key] = (Image.open(BytesIO(response.content)))
    return images

# %%
STARTING_RATIO = 4 
RATIO_STEP = 1
SUBSAMPLE_RATIOS = (np.arange(STARTING_RATIO, 10, RATIO_STEP)/ 10).tolist()  + [0.93, 0.96, 0.99, 1]
FILE_NAME = 'Polymore.json'
#RATIO_TO_SAVE = 0.7
IOU_TO_STOP = 0.9
VISUALIZE = True
ASSETS_TO_VISUALIZE = 5
f = open(FILE_NAME, encoding='utf-8')
data_origin = json.load(f)
original_size = getsizeof(json.dumps(data_origin, indent = 2))
visualized_assets = np.random.randint(1, len(data_origin) - 1 , ASSETS_TO_VISUALIZE )
avg_ious = []
avg_poly_lens = []
avg_by_class = {}
sizes = []
original_polys = {}
new_polys = {}
run = 0
ratio_found = False
json_to_save = None
# %%
# Process
print(f"Running Simplification over {FILE_NAME} for Ratios: {SUBSAMPLE_RATIOS}")
for ratio in SUBSAMPLE_RATIOS:
    print(f"* Run for Simplification ratio {'{:.2f}'.format(ratio)}")
    ious = []
    poly_lens = []
    poly_category_lens = {}
    iou_category = {}
    data = copy.deepcopy(data_origin)
    asset_counter = 0
    pick_asset_polygon = False
    for asset in data:
        asset_counter += 1
        if asset_counter in visualized_assets:
            pick_asset_polygon = True
        for tasks in asset['tasks']:
            for obj in tasks['objects']:
                if 'polygon' in obj:
                    category = obj['title']
                    old_poly = obj['polygon']
                    new_poly = simplify_polygon(old_poly, ratio).tolist()                   
                    if pick_asset_polygon:
                        original_polys[asset_counter] = old_poly
                        if asset_counter in new_polys:
                            new_polys[asset_counter].append(new_poly)
                        else:
                            new_polys[asset_counter] = [new_poly]
                        pick_asset_polygon = False
                    iou = calculate_iou(old_poly, new_poly)
                    ious.append(iou) 
                    poly_lens.append(len(new_poly))
                    if category in poly_category_lens:
                        poly_category_lens[category].append(len(new_poly))
                        iou_category[category].append(iou)
                    else:
                        poly_category_lens[category] = [len(new_poly)]
                        iou_category[category] = [iou]
                    obj['polygon'] = new_poly
    mean_iou = statistics.mean(ious)
    avg_ious.append( mean_iou)
    avg_poly_lens.append(statistics.mean(poly_lens))
    avg_by_class[ratio] = {}
    for key in poly_category_lens:
        avg_by_class[ratio][key] = {}
        avg_by_class[ratio][key]['len'] = statistics.mean(poly_category_lens[key]) 
        avg_by_class[ratio][key]['iou'] = statistics.mean(iou_category[key]) 
    json_object = json.dumps(data, indent = 2)
    sizes.append(getsizeof(json_object))
    run += 1
    if mean_iou >= IOU_TO_STOP and not ratio_found:
        print(f"Simplifcation Ratio Found: IOU requirement of {IOU_TO_STOP} was satisfied at simplification ratio of {ratio} ")
        ratio_found = True
        json_to_save = copy.deepcopy(json_object)


# %%
ratios_to_visualize = [0.5,0.8,1.0]
# Visualize Plots
visualize_line_plotly(x=SUBSAMPLE_RATIOS, y=avg_ious, title="Information Loss chart - Average IOUs", yLabel="IOU" )
visualize_line_plotly(x=SUBSAMPLE_RATIOS, y=sizes, title="Size Reduction Chart", yLabel="Size (bytes)" )
visualize_line_plotly(x=sizes, y=avg_ious, title="Sizes vs IOUs", xLabel="Size (bytes)", yLabel="IOU")
visualize_stats_by_class(avg_by_class, ratios_to_visualize, metric='iou')
visualize_stats_by_class(avg_by_class, ratios_to_visualize, metric='len', title='Polygon Size of Objects by Class for Various Ratios', xLabel='Class Name', yLabel='Average Polygon Size')
# %% 
# Fetch images Overlays
print("Fetching & Saving Benchmark Images - For Comparitive Visualization of various simplification rates")
imgs =  fetch_benchmark_assets(visualized_assets, data_origin)

# %% 
# Visualize Overlays
for key in visualized_assets:
    polygon_on_image(original_polys[key], copy.deepcopy(imgs[key]) , show=False, save_title=f"Asset_{key}_Original_Polygon.jpeg") 

    ratio_index = 0
    for poly in new_polys[key]:
        polygon_on_image(poly, copy.deepcopy(imgs[key]), show=False, save_title=f"Asset_{key}_Subsampeled_{'{:.2f}'.format(SUBSAMPLE_RATIOS[ratio_index])}_Polygon.jpeg") 
        ratio_index += 1
# %%
# Write to File
print(f"Saving to file: Subsampled {FILE_NAME}")
with open(f"Subsampled {FILE_NAME}", "w") as outfile:
    outfile.write(json_to_save)
