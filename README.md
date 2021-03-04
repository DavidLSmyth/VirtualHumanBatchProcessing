# Blender Synthetic Data Generation
This repo contains a set of scripts for blender that can be used to automate tasks such as re-targeting related to 3D geometry. The aim is to use this synthetic data for tasks such as shape estimation that typically use Neural Networks.
It can also generate some test data where ground truth is accurately known (e.g. pose, shape, camera intrinsics/extrinsics), which can be used for sanity checking models.

## Why Blender?
In order to process 3D geometry, it's necessary to read in data, process that data and the export, where import and export is supported in a range of formats. Processing should be supported by a high-level api. Blender provides this functionality and is free and open-sourced


## Summary of Functions
The following high-level functions can all be performed as batch processes, allowing the creation of large synthetic datasets.

1. Format Conversion

    The blender api breaks up the import/export of models into the different paradigms:  
    1. [Import Scene Operators](https://docs.blender.org/api/2.83/bpy.ops.import_scene.html)
    2. [Import Anim Operators](https://docs.blender.org/api/current/bpy.ops.import_anim.html)
    3. [Import Curve Operators](https://docs.blender.org/api/current/bpy.ops.import_curve.html)
    4. [Import Mesh Operators](https://docs.blender.org/api/current/bpy.ops.import_mesh.html)

    Each of these groups have similar import/export params

2. Animation Re-targeting

    Animation re-targeting is done using Rokoko studio: https://github.com/Rokoko/rokoko-studio-live-blender.

3. Texture Atlasing

    Texture atlasing is done using the CATS repository: https://github.com/GiveMeAllYourCats/cats-blender-plugin, modified so the API can be called from a script. This can be useful to work with a single texture with a neural network.

4. Simple Scene Composition and Rendering

    Scenes can be composed using scripts to place cameras, lights, etc. For batch rendering, the blenderProc repository https://github.com/DLR-RM/BlenderProc is a more suitable tool, but we provide some basic functionality in this repository.

## Supported Existing Data
Existing assets that we have tested that are compatible (or partially compatible) with this repository include:
1. Mixamo (https://www.mixamo.com/)
2. Microsoft Rocketbox (https://github.com/microsoft/Microsoft-Rocketbox)
3. CMU mocap (http://mocap.cs.cmu.edu/)
4. The VG resource (https://www.models-resource.com/)

## Installation
To use this repository:
1. Install the zips in blenderZips in blender
2. Create a virtual environment and run `pip install -r requirements.txt`
3. You should then be able to run the examples in example_scripts.

## Usage Patterns
Most synthetic data generation pipelines look something like the following:

<pipeline diagram>

Rendering is usually a nuanced and important factor which we would recommend be deferred to a repository such as BlenderProc. Therefore, a typical usage pattern to generate synthetic data up to the rendering stage is as follows:

1. For each model in your dataset:
2. Load your model (usually fbx/obj).
3. Process the model (e.g. re-target an animation to the loaded mesh).
4. Clean up any unnecessary intermediate artifacts.
5. Export the result (e.g. objs of individual frames, a re-targeted fbx, etc.) which is ready to be used directly in a scene that will be rendered.
6. Reset to the scene.
