# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
#  SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from omni.isaac.kit import SimulationApp
import os
import argparse

parser = argparse.ArgumentParser("Dataset generator")
parser.add_argument("--headless", type=bool, default=False, help="Launch script headless, default is False")
parser.add_argument("--height", type=int, default=544, help="Height of image")
parser.add_argument("--width", type=int, default=960, help="Width of image")
parser.add_argument("--num_frames", type=int, default=1000, help="Number of frames to record")
parser.add_argument("--rt_subframes", type=int, default=10, help="Number of subframes for each frame to get better rendering quality")
parser.add_argument("--distractors", type=str, default="warehouse", 
                    help="Options are 'warehouse' (default), 'additional' or None")
parser.add_argument("--ws_dir", type=str, default=os.getcwd(), 
                    help="Workspace directory")
parser.add_argument("--data_dir", type=str, default=os.getcwd() + "/_kitchenware_data", 
                    help="Location where data will be output")

args, unknown_args = parser.parse_known_args()

# print the args
print(f'args: {args}')

# This is the config used to launch simulation. 
CONFIG = {"renderer": "RayTracedLighting", "headless": args.headless, 
          "width": args.width, "height": args.height,
          "num_frames": args.num_frames,
          "rt_subframes": args.rt_subframes}

simulation_app = SimulationApp(launch_config=CONFIG)


## This is the path which has the background scene in which objects will be added.
ENV_URL = "/Isaac/Environments/Simple_Warehouse/warehouse.usd"
KITCHEN_URL = "omniverse://192.168.22.214/ShenNongShi/SNS-Kitchen_Scene/Collected_sns_emily_wok/kitchen_scene.usd"

import carb
import yaml
import time
import omni
import omni.usd
from omni.isaac.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import get_current_stage, open_stage
# from pxr import Semantics
import Semantics

import omni.replicator.core as rep

from omni.isaac.core.utils.semantics import get_semantics

from pxr import Usd, UsdGeom, Sdf

# This is the location of the palletjacks in the simready asset library
# PALLETJACKS = ["http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/DigitalTwin/Assets/Warehouse/Equipment/Pallet_Trucks/Scale_A/PalletTruckScale_A01_PR_NVD_01.usd",
#             "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/DigitalTwin/Assets/Warehouse/Equipment/Pallet_Trucks/Heavy_Duty_A/HeavyDutyPalletTruck_A01_PR_NVD_01.usd",
#             "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/DigitalTwin/Assets/Warehouse/Equipment/Pallet_Trucks/Low_Profile_A/LowProfilePalletTruck_A01_PR_NVD_01.usd"]
KITCHEN_ASSETS_LIST_PATH = args.ws_dir + "/kitchen_asset_list.yaml"
KITCHEN_ASSETS_LIST = yaml.load(open(KITCHEN_ASSETS_LIST_PATH), Loader=yaml.FullLoader)
# append the workspace directory to the kitchenware asset paths
# KITCHEN_ASSETS_LIST['kitchenware_path'] = [os.path.join(args.ws_dir, asset_path) for asset_path in KITCHEN_ASSETS_LIST['kitchenware_path']]
# # append `file://` to the asset paths
# KITCHEN_ASSETS_LIST['kitchenware_path'] = ['file://' + asset_path for asset_path in KITCHEN_ASSETS_LIST['kitchenware_path']]
print(f"KITCHEN_ASSETS_LIST: {KITCHEN_ASSETS_LIST}")

# The warehouse distractors which will be added to the scene and randomized
DISTRACTORS_WAREHOUSE = 2 * ["/Isaac/Environments/Simple_Warehouse/Props/S_TrafficCone.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/S_WetFloorSign.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_A_01.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_A_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_A_03.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_B_01.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_B_01.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_B_03.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BarelPlastic_C_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BottlePlasticA_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BottlePlasticB_01.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BottlePlasticA_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BottlePlasticA_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BottlePlasticD_01.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BottlePlasticE_01.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_BucketPlastic_B.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01_1262.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01_1268.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01_1482.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01_1683.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01_291.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01_1454.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01_1513.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CratePlastic_A_04.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CratePlastic_B_03.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CratePlastic_B_05.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CratePlastic_C_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_CratePlastic_E_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_PushcartA_02.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_RackPile_04.usd",
                            "/Isaac/Environments/Simple_Warehouse/Props/SM_RackPile_03.usd"]


## Additional distractors which can be added to the scene
DISTRACTORS_ADDITIONAL = ["/Isaac/Environments/Hospital/Props/Pharmacy_Low.usd",
                        "/Isaac/Environments/Hospital/Props/SM_BedSideTable_01b.usd",
                        "/Isaac/Environments/Hospital/Props/SM_BooksSet_26.usd",
                        "/Isaac/Environments/Hospital/Props/SM_BottleB.usd",
                        "/Isaac/Environments/Hospital/Props/SM_BottleA.usd",
                        "/Isaac/Environments/Hospital/Props/SM_BottleC.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Cart_01a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Chair_02a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Chair_01a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Computer_02b.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Desk_04a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_DisposalStand_02.usd",
                        "/Isaac/Environments/Hospital/Props/SM_FirstAidKit_01a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_GasCart_01c.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Gurney_01b.usd",
                        "/Isaac/Environments/Hospital/Props/SM_HospitalBed_01b.usd",
                        "/Isaac/Environments/Hospital/Props/SM_MedicalBag_01a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Mirror.usd",
                        "/Isaac/Environments/Hospital/Props/SM_MopSet_01b.usd",
                        "/Isaac/Environments/Hospital/Props/SM_SideTable_02a.usd",
                        "/Isaac/Environments/Hospital/Props/SM_SupplyCabinet_01c.usd",
                        "/Isaac/Environments/Hospital/Props/SM_SupplyCart_01e.usd",
                        "/Isaac/Environments/Hospital/Props/SM_TrashCan.usd",
                        "/Isaac/Environments/Hospital/Props/SM_Washbasin.usd",
                        "/Isaac/Environments/Hospital/Props/SM_WheelChair_01a.usd",
                        "/Isaac/Environments/Office/Props/SM_WaterCooler.usd",
                        "/Isaac/Environments/Office/Props/SM_TV.usd",
                        "/Isaac/Environments/Office/Props/SM_TableC.usd",
                        "/Isaac/Environments/Office/Props/SM_Recliner.usd",
                        "/Isaac/Environments/Office/Props/SM_Personenleitsystem_Red1m.usd",
                        "/Isaac/Environments/Office/Props/SM_Lamp02_162.usd",
                        "/Isaac/Environments/Office/Props/SM_Lamp02.usd",
                        "/Isaac/Environments/Office/Props/SM_HandDryer.usd",
                        "/Isaac/Environments/Office/Props/SM_Extinguisher.usd"]


# The textures which will be randomized for the wall and floor
TEXTURES = ["/Isaac/Materials/Textures/Patterns/nv_asphalt_yellow_weathered.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_tile_hexagonal_green_white.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_rubber_woven_charcoal.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_granite_tile.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_tile_square_green.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_marble.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_brick_reclaimed.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_concrete_aged_with_lines.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_wooden_wall.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_stone_painted_grey.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_wood_shingles_brown.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_tile_hexagonal_various.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_carpet_abstract_pattern.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_wood_siding_weathered_green.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_animalfur_pattern_greys.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_artificialgrass_green.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_bamboo_desktop.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_brick_reclaimed.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_brick_red_stacked.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_fireplace_wall.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_fabric_square_grid.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_granite_tile.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_marble.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_gravel_grey_leaves.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_plastic_blue.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_stone_red_hatch.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_stucco_red_painted.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_rubber_woven_charcoal.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_stucco_smooth_blue.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_wood_shingles_brown.jpg",
            "/Isaac/Materials/Textures/Patterns/nv_wooden_wall.jpg"]


def update_semantics(stage, keep_semantics=[]):
    """ Remove semantics from the stage except for keep_semantic classes"""
    for prim in stage.Traverse():
        if prim.HasAPI(Semantics.SemanticsAPI):
            processed_instances = set()
            for property in prim.GetProperties():
                is_semantic = Semantics.SemanticsAPI.IsSemanticsAPIPath(property.GetPath())
                if is_semantic:
                    instance_name = property.SplitName()[1]
                    if instance_name in processed_instances:
                        # Skip repeated instance, instances are iterated twice due to their two semantic properties (class, data)
                        continue
                    
                    processed_instances.add(instance_name)
                    sem = Semantics.SemanticsAPI.Get(prim, instance_name)
                    type_attr = sem.GetSemanticTypeAttr()
                    data_attr = sem.GetSemanticDataAttr()

                    # Check for our data classes needed for the model
                    if data_attr.Get() in keep_semantics:
                        continue
                    else:
                        # remove semantics of all other prims
                        prim.RemoveProperty(type_attr.GetName())
                        prim.RemoveProperty(data_attr.GetName())
                        prim.RemoveAPI(Semantics.SemanticsAPI, instance_name)
    

# needed for loading textures correctly
def prefix_with_isaac_asset_server(relative_path):
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        raise Exception("Nucleus server not found, could not access Isaac Sim assets folder")
    return assets_root_path + relative_path


def full_distractors_list(distractor_type="warehouse"):
    """Distractor type allowed are warehouse, additional or None. They load corresponding objects and add
    them to the scene for DR"""
    full_dist_list = []

    if distractor_type == "warehouse":
        for distractor in DISTRACTORS_WAREHOUSE:
            full_dist_list.append(prefix_with_isaac_asset_server(distractor))
    elif distractor_type == "additional":
        for distractor in DISTRACTORS_ADDITIONAL:
            full_dist_list.append(prefix_with_isaac_asset_server(distractor))
    else:
        print("No Distractors being added to the current scene for SDG")

    return full_dist_list


def full_textures_list():
    full_tex_list = []
    for texture in TEXTURES:
        full_tex_list.append(prefix_with_isaac_asset_server(texture))

    return full_tex_list


def add_static_kitchenware():
    """Add fixed position kitchenware assets"""
    stage = get_current_stage()
    
    fixed_assets = {
        'wok': {
            'position': (1.09759, -0.00701, 0.87748),
            'rotation': (-3.77, -2.497, 121.597)
        },
        'ladle': {
            'position': (1.03484, -0.47611, 0.98812),
            'rotation': (0, -10, 0)
        }
    }
    
    for category, data in KITCHEN_ASSETS_LIST['kitchenware_path'].items():
        if category in fixed_assets:
            paths = data['paths']
            scale_value = data['scale']
            
            print(f'Adding fixed position object: {category} to position {fixed_assets[category]["position"]} with rotation {fixed_assets[category]["rotation"]} and scale {scale_value}')
            
            fixed_prim_path = f"/World/fixed_{category}"
            fixed_prim = stage.DefinePrim(fixed_prim_path, "Xform")
            fixed_ref = fixed_prim.GetReferences()
            fixed_ref.AddReference(paths[0])
            
            # Add semantics
            sem = Semantics.SemanticsAPI.Apply(fixed_prim, "semantics")
            sem.CreateSemanticTypeAttr("class")
            sem.CreateSemanticDataAttr(category)
            
            xformable = UsdGeom.Xformable(fixed_prim)
            
            # Remove existing transform if any
            for name in fixed_prim.GetPropertyNames():
                if name == "xformOp:transform":
                    fixed_prim.RemoveProperty(name)
            
            # Handle translation
            if "xformOp:translate" in fixed_prim.GetPropertyNames():
                translate_op = UsdGeom.XformOp(fixed_prim.GetAttribute("xformOp:translate"))
            else:
                translate_op = xformable.AddXformOp(UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.PrecisionDouble, "")
            
            # Handle rotation
            if "xformOp:rotateXYZ" in fixed_prim.GetPropertyNames():
                rotate_op = UsdGeom.XformOp(fixed_prim.GetAttribute("xformOp:rotateXYZ"))
            else:
                rotate_op = xformable.AddXformOp(UsdGeom.XformOp.TypeRotateXYZ, UsdGeom.XformOp.PrecisionDouble, "")
            
            # Handle scale
            if "xformOp:scale" in fixed_prim.GetPropertyNames():
                scale_op = UsdGeom.XformOp(fixed_prim.GetAttribute("xformOp:scale"))
            else:
                scale_op = xformable.AddXformOp(UsdGeom.XformOp.TypeScale, UsdGeom.XformOp.PrecisionDouble, "")
            
            xformable.SetXformOpOrder([translate_op, rotate_op, scale_op])
            
            translate_op.Set(fixed_assets[category]['position'])
            rotate_op.Set(fixed_assets[category]['rotation'])
            scale_op.Set((scale_value, scale_value, scale_value))

def add_dynamic_kitchenware():
    """Add randomly positioned kitchenware assets"""
    rep_obj_list = []
    fixed_assets = {'wok', 'ladle'}  # Skip these as they're handled by static placement
    
    for category, data in KITCHEN_ASSETS_LIST['kitchenware_path'].items():
        paths = data['paths']
        scale_value = data['scale']
        for path in paths:
            obj = rep.create.from_usd(path, semantics=[("class", category)], count=5)
            with obj:
                rep.modify.pose(scale=(scale_value, scale_value, scale_value))
            rep_obj_list.append(obj)
    if not rep_obj_list:
        print("Warning: No kitchenware assets found for random placement.")
        print("Warning: No kitchenware assets found. Check KITCHEN_ASSETS_LIST['kitchenware_path'].")
    rep_kitchenware_group = rep.create.group(rep_obj_list)
    return rep_kitchenware_group


def add_distractors(distractor_type="warehouse"):
    full_distractors = full_distractors_list(distractor_type)
    distractors = [rep.create.from_usd(distractor_path, count=1) for distractor_path in full_distractors]
    distractor_group = rep.create.group(distractors)
    return distractor_group


# This will handle replicator
def run_orchestrator():

    rep.orchestrator.run()

    # Wait until started
    while not rep.orchestrator.get_is_started():
        simulation_app.update()

    # Wait until stopped
    while rep.orchestrator.get_is_started():
        simulation_app.update()

    rep.BackendDispatch.wait_until_done()
    rep.orchestrator.stop()


def main():
    # Open the environment in a new stage
    print(f"Loading Stage {ENV_URL}")
    open_stage(prefix_with_isaac_asset_server(ENV_URL))
    stage = get_current_stage()

    # Add the kitchen scene
    print(f"Adding Kitchen Scene {KITCHEN_URL}")
    kitchen_prim = stage.DefinePrim("/World/kitchen", "Xform")
    kitchen_ref = kitchen_prim.GetReferences()
    kitchen_ref.AddReference(KITCHEN_URL)

    # Adjust the kitchen position and scale if needed
    xform = UsdGeom.Xformable(kitchen_prim)
    xform.AddTranslateOp().Set((0, 0, 0))  # Adjust position as needed
    xform.AddScaleOp().Set((1, 1, 1))  # Adjust scale as needed
    
    # Run some app updates to make sure things are properly loaded
    for i in range(100):
        if i % 10 == 0:
            print(f"App update {i}..")
        simulation_app.update()


    textures = full_textures_list()
    
    # Add both static and dynamic kitchenware
    add_static_kitchenware()
    rep_dynamic_kitchenware = add_dynamic_kitchenware()
    rep_distractor_group = add_distractors(distractor_type=args.distractors)

    # We only need labels for the kitchenware objects
    update_semantics(stage=stage, keep_semantics=KITCHEN_ASSETS_LIST['kitchenware_path'].keys())

    # Create camera with Replicator API for gathering data
    cam = rep.create.camera(clipping_range=(0.1, 1000000))

    # trigger replicator pipeline
    with rep.trigger.on_frame(max_execs=CONFIG["num_frames"], rt_subframes=CONFIG["rt_subframes"]):

        # Move the camera around in the scene, focus on the center of warehouse
        with cam:
            rep.modify.pose(position=rep.distribution.uniform((-4, -4, 1.2), (4, 4, 2)),
                            # look_at=(0, 0, 0.8))
                            look_at=rep.distribution.uniform((-1, -1, 0.4), (1, 1, 1.6)))

        # Get the Kitchenware metal mesh and modify its color
        # with rep.get.prims(path_pattern="metal"):
        #     rep.randomizer.color(colors=rep.distribution.uniform((0, 0, 0), (0.2, 0.2, 0.2)))

        # Only randomize the dynamic kitchenware
        if rep_dynamic_kitchenware is not None:
            with rep_dynamic_kitchenware:
                rep.modify.pose(position=rep.distribution.uniform((-2, -2, 0.4), (2, 2, 1.2)),
                                rotation=rep.distribution.uniform((0, 0, 0), (180, 180, 360)))
                                # scale=rep.distribution.uniform((0.01, 0.01, 0.01), (0.01, 0.01, 0.01)))
                                # scale=rep.distribution.uniform((1, 1, 1), (1, 1, 1)))

        # Modify the pose of all the distractors in the scene
        with rep_distractor_group:
            rep.modify.pose(position=rep.distribution.uniform((-6, -6, 0), (6, 12, 0)),
                                rotation=rep.distribution.uniform((0, 0, 0), (0, 0, 360)),
                                scale=rep.distribution.uniform(1, 1.5))
        
        # Randomize the lighting of the scene
        with rep.get.prims(path_pattern="RectLight"):
            # rep.modify.attribute("color", rep.distribution.uniform((0, 0, 0), (1, 1, 1)))
            rep.modify.attribute("color", rep.distribution.normal((0.5, 0.5, 0.5), (0.2, 0.2, 0.2)))
            rep.modify.attribute("intensity", rep.distribution.normal(10000.0, 300000.0))
            rep.modify.visibility(rep.distribution.choice([True, True, True, True, False, False, False]))

        # select floor material
        random_mat_floor = rep.create.material_omnipbr(diffuse_texture=rep.distribution.choice(textures),
                                                    roughness=rep.distribution.uniform(0, 1),
                                                    metallic=rep.distribution.choice([0, 1]),
                                                    emissive_texture=rep.distribution.choice(textures),
                                                    emissive_intensity=rep.distribution.uniform(0, 1000),)
        
        
        with rep.get.prims(path_pattern="SM_Floor"):
            rep.randomizer.materials(random_mat_floor)

        # select random wall material
        random_mat_wall = rep.create.material_omnipbr(diffuse_texture=rep.distribution.choice(textures),
                                                    roughness=rep.distribution.uniform(0, 1),
                                                    metallic=rep.distribution.choice([0, 1]),
                                                    emissive_texture=rep.distribution.choice(textures),
                                                    emissive_intensity=rep.distribution.uniform(0, 1000),)

        
        with rep.get.prims(path_pattern="SM_Wall"):
            rep.randomizer.materials(random_mat_wall)


    # Set up the writer
    writer = rep.WriterRegistry.get("KittiWriter")

    # output directory of writer
    output_directory = args.data_dir
    print("Outputting data to ", output_directory)

    # use writer for bounding boxes, rgb and segmentation
    writer.initialize(output_dir=output_directory,
                    omit_semantic_type=True,
                    colorize_instance_segmentation=True)


    # attach camera render products to wrieter so that data is outputted
    RESOLUTION = (CONFIG["width"], CONFIG["height"])
    render_product  = rep.create.render_product(cam, RESOLUTION)
    writer.attach(render_product)

    # run rep pipeline
    run_orchestrator()
    simulation_app.update()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        carb.log_error(f"Exception: {e}")
        import traceback

        traceback.print_exc()
    finally:
        simulation_app.close()


