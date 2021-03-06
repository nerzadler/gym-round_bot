#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Cressot Loic
    ISIR - CNRS / Sorbonne Université
    02/2018

    This file allows to build worlds
    TODO : replace this file by a .json loader and code worlds in .json
""" 

# WARNING : don't fo (from round_bot_py import round_bot_model) here to avoid mutual imports !

import os

def _texture_path(texture_bricks_name):
    """
    Parameter
    ---------
    texture_bricks_name : str
        name of the world main texture 

    Return
    ------
    texture_path: (str) path corresponding to the texture_bricks_name

    Raises
    ------
    ValueError : raised if texture_bricks_name is unkwnonw
    """
    if texture_bricks_name == 'minecraft':
        return '/textures/texture_minecraft.png'
    elif texture_bricks_name == 'graffiti':
        return '/textures/texture_graffiti.png'
    elif texture_bricks_name == 'colours':
        return '/textures/texture_colours.png'
    else :
        raise ValueError('Unknown texture name '+ texture_bricks_name + ' in loading world')


def _build_square_default_world(model, texture_bricks_name, width=45, depth=45, hwalls=4, dwalls=1,                    
                            texture_robot='/textures/robot.png',
                            texture_visualisation='/textures/visualisation.png',
                            texture_distractors='/textures/texture_distractors.png',
                            wall_reward=-1,
                            distractors=False,
                            distractors_speed=0.1,
                            sandboxes=False,
                            trigger_button=False,                 
                            ):
    """
    Builds a simple rectangle planar world with walls around

    Parameters
    ----------
    - model : (round_bot_model.Model) model to load world in
    - texture_bricks_name : (str) name of the texture for the bricks
    - width : (int) width of the world
    - depth : (int) depth of the world
    - hwalls : (int) heigh of walls    
    - dwalls: (int) depth of walls
    - texture_bricks, texture_robot, texture_visualisation : (string)
        paths for texture image of bricks, robot and visualisation
    - wall_reward : (float) reward for wall collision
    - distractors (Bool) : add visual distractors on walls and ground
    - distractors_speed (float) : speed of visual distractors displacement
    - sandboxes (Bool) : add sandboxes ont the ground (slowing down the robot when crossed)
    - trigger_button (Bool) : add a trigger button that will trigger a change in the environment (change to be defined)

    Returns
    -------
    world information
    """
    texture_bricks = _texture_path(texture_bricks_name)
    
    # TODO : better import would be global and without "from" but doesn't work for the moment
    from gym_round_bot.envs import round_bot_model 
    # create textures coordinates
    GRASS = round_bot_model.Block.tex_coords((1, 0), (0, 1), (0, 0))
    SAND = round_bot_model.Block.tex_coords((1, 1), (1, 1), (1, 1))
    BRICK = round_bot_model.Block.tex_coords((2, 0), (2, 0), (2, 0))
    BRICK2 = round_bot_model.Block.tex_coords((0, 2), (0, 2), (0, 2))
    STONE = round_bot_model.Block.tex_coords((2, 1), (2, 1), (2, 1))
    STONE2 = round_bot_model.Block.tex_coords((1, 2), (1, 2), (1, 2))
    BUTTON = round_bot_model.Block.tex_coords((2, 2), (2, 2), (2, 2))
    DISTRACTORS = [ round_bot_model.Block.tex_coords(t,t,t) for t in [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(2,0)] ]

    nw = width/2.0  # 1/2 width of this world
    nd = depth/2.0  # 1/2 depth of this world
    wr = width/3.0 # wr width of reward area
    wwalls = width

    # get texture paths in current directory
    brick_texture_path = os.path.dirname(__file__) + texture_bricks
    robot_texture_path = os.path.dirname(__file__) + texture_robot
    visualisation_texture_path = os.path.dirname(__file__) + texture_visualisation
    distractors_texture_path = os.path.dirname(__file__) + texture_distractors
    texture_paths = {'brick':brick_texture_path,
                     'robot':robot_texture_path,
                     'visualisation':visualisation_texture_path,
                     'distractors':distractors_texture_path,
                      }   

    # Build gound block
    ground_block = model.add_block( (0, -3, 0, 2*nd, 6, 2*nw, 0.0, 0.0, 0.0), GRASS, block_type='brick')


    # Build wall blocks with negative reward on collision
    #front wall
    back_wall_block = model.add_block( (0, hwalls/2, -nw, depth, hwalls, dwalls, 0.0, 0.0, 0.0),
                     texture=BRICK, block_type='brick', collision_reward = wall_reward)
    #back wall
    front_wall_block = model.add_block( (0, hwalls/2, nw, depth, hwalls, dwalls, 0.0, 0.0, 0.0),
                     texture=STONE2, block_type='brick', collision_reward = wall_reward)
    #left wall
    left_wall_block = model.add_block( (-nd, hwalls/2, 0, dwalls, hwalls, wwalls, 0.0, 0.0, 0.0),
                     texture=STONE, block_type='brick', collision_reward = wall_reward)
    #right wall
    right_wall_block = model.add_block( (nd, hwalls/2, 0, dwalls, hwalls, wwalls, 0.0, 0.0, 0.0),
                     texture=BRICK2, block_type='brick', collision_reward = wall_reward)

    
    if distractors:
        # add visual distractors on the groud and inner faces of walls if asked

        # distractor ground block
        size_ground_distractor = n = min(nw,nd)
        ground_bb = round_bot_model.BoundingBoxBlock( (0, 0.1, 0), (2*n, 0, 2*n), (0.0, 0.0, 0.0), linked_block=ground_block)
        model.add_block( components=(0, 0, 0, size_ground_distractor, 0.0, size_ground_distractor, 0.0, 0.0, 0.0),
                         texture=DISTRACTORS[0], block_type='flat_distractor', boundingBox = ground_bb, speed=distractors_speed)
        model.add_block( components=(0, 0, 0, size_ground_distractor, 0.0, size_ground_distractor, 0.0, 0.0, 0.0),
                         texture=DISTRACTORS[0], block_type='flat_distractor', boundingBox = ground_bb, speed=distractors_speed)
        # wall distractors :
        width_wall_distractors = wwalls/2
        height_wall_distractors = hwalls*2/3
        # distractor back_wall inner face block
        back_wall_bb = round_bot_model.BoundingBoxBlock( (0, hwalls/2, -nw+dwalls/2+0.1), (wwalls, height_wall_distractors, 0.0), (0.0, 0.0, 0.0), linked_block=ground_block)
        model.add_block( components=(0, 0, 0, width_wall_distractors, height_wall_distractors, 0.0, 0.0, 0.0, 0.0),
                         texture=DISTRACTORS[1], block_type='flat_distractor', boundingBox = back_wall_bb, speed=distractors_speed)
        # distractor front_wall inner face block
        front_wall_bb = round_bot_model.BoundingBoxBlock(( 0, hwalls/2, nw-dwalls/2-0.1), (wwalls, height_wall_distractors, 0.0), (0.0, 0.0, 0.0), linked_block=ground_block)
        model.add_block( components=(0, 0, 0, width_wall_distractors, height_wall_distractors, 0.0, 0.0, 0.0, 0.0),
                         texture=DISTRACTORS[2], block_type='flat_distractor', boundingBox = front_wall_bb, speed=distractors_speed)
        # distractor left_wall inner face block
        left_wall_bb = round_bot_model.BoundingBoxBlock( (-nd+dwalls/2+0.1, hwalls/2, 0), (0.0, height_wall_distractors, wwalls), (0.0, 0.0, 0.0), linked_block=ground_block)
        model.add_block( components=(0, 0, 0, 0.0, height_wall_distractors, width_wall_distractors, 0.0, 0.0, 0.0),
                         texture=DISTRACTORS[3], block_type='flat_distractor', boundingBox = left_wall_bb, speed=distractors_speed)
        # distractor right_wall inner face block
        right_wall_bb = round_bot_model.BoundingBoxBlock(( nd-dwalls/2-0.1, hwalls/2, 0), (0.0, height_wall_distractors, wwalls), (0.0, 0.0, 0.0), linked_block=ground_block)
        model.add_block( components=(0, 0, 0, 0.0, height_wall_distractors, width_wall_distractors, 0.0, 0.0, 0.0),
                         texture=DISTRACTORS[4], block_type='flat_distractor', boundingBox = right_wall_bb, speed=distractors_speed)


    if sandboxes :
        # add sandboxes ont the ground if asked (slowing down the robot when crossed)
        model.add_block( (0, 0.3, 0, nd/2, 0, nw/2, 0.0, 0.0, 0.0), SAND, block_type='sandbox')

    if trigger_button :
        # add a trigger button that will trigger a change in the world when crossed ON / OFF
        #TRIGGER = round_bot_model.Block.tex_coords((1, 0), (1, 0), (1, 0))
        model.add_block( (0, 0.3, 0, nw/3, 0.2, nw/3, 0.0, 0.0, 0.0), BUTTON, block_type='trigger_button')


    world_info = {  'width' : 2*nw,
                    'depth' : 2*nd,
    }

    return texture_paths, world_info



def build_square_world(model, texture, robot_diameter=2 ,width=45, depth=45, hwalls=4, dwalls=1, wall_reward=-1, goal_reward=10, distractors=False,
                    distractors_speed=0.1, sandboxes=False, trigger_button=False, visible_reward=False):
    """
    Builds the square world
    """    
    ## first build default world
    texture_paths, world_info = _build_square_default_world(model, texture, width=width, depth=depth,
                                                        hwalls=hwalls, dwalls=dwalls,
                                                        wall_reward=wall_reward, distractors=distractors,
                                                        distractors_speed=distractors_speed,
                                                        sandboxes=sandboxes, trigger_button=trigger_button,)

    ## then add specs
    from gym_round_bot.envs import round_bot_model
    BOT = round_bot_model.Block.tex_coords((0, 0), (0, 1), (0, 1))
    START = round_bot_model.Block.tex_coords((0, 0), (0, 0), (0, 0))
    REWARD = round_bot_model.Block.tex_coords((0, 1), (0, 1), (0, 1))

    nw = width/2.0  # 1/2 width of this world
    nd = depth/2.0  # 1/2 depth of this world
    wwalls = width # width of walls
    wr = width/4.0 # wr width of reward area
   
    # set robot specifications
    bot_radius = robot_diameter/2.0
    bot_height = bot_radius

    # Build reward block in the corner
    rew = model.add_block( (nd-(wr/2+dwalls/2), bot_height/2.0, -nw+(wr/2+dwalls/2), wr, bot_height/3.0, wr, 0.0, 0.0, 0.0),
                     texture=REWARD, block_type='reward', collision_reward = goal_reward, visible=visible_reward)
    # Build robot block, set initial height to bot_heigh/2 + small offset to avoid ground collision
    model.add_block( (0, bot_height/2.0+0.1, 0, 2*bot_radius, bot_height, 2*bot_radius, 0.0, 0.0, 0.0),
                     texture=BOT, block_type='robot')
    # add starting areas (the height=0 of block does not matter here, only area of (hwalls-2*dwalls)^2)
    model.add_block( (0, bot_height/2.0+0.1, 0, 2*nd-2*dwalls, 0.1, 2*nw-2*dwalls, 0.0, 0.0, 0.0),
                     texture=START, block_type='start')

    return texture_paths, world_info



def build_square_1wall_world(model, texture, robot_diameter=2, width=45, depth=45, hwalls=2, dwalls=2, wall_reward=-1, goal_reward=10, distractors=False,
                          distractors_speed=0.1, sandboxes=False, trigger_button=False, visible_reward=False):
    """
    Builds a simple rectangle planar world with walls around, and 1 wall in the middle
    """
    ## first build default world
    texture_paths, world_info = _build_square_default_world(model, texture, width=width, depth=depth,
                                                        hwalls=hwalls, dwalls=dwalls,
                                                        wall_reward=wall_reward, distractors=distractors,
                                                        distractors_speed=distractors_speed,
                                                        sandboxes=sandboxes, trigger_button=trigger_button,)

    ## then add specs
    from gym_round_bot.envs import round_bot_model
    BOT = round_bot_model.Block.tex_coords((0, 0), (0, 1), (0, 1))
    START = round_bot_model.Block.tex_coords((0, 0), (0, 0), (0, 0))
    REWARD = round_bot_model.Block.tex_coords((0, 1), (0, 1), (0, 1))
    SAND = round_bot_model.Block.tex_coords((1, 1), (1, 1), (1, 1))

    n = width/2.0  # 1/2 width and depth of world
    wwalls = 2*n # width of walls
    wr = width/4.0 # wr width of reward area
 
    # set robot specifications
    bot_radius = robot_diameter/2.0
    bot_height = bot_radius
    
    # middle wall
    model.add_block( (n/2, hwalls/2, -n/4, wwalls/2, hwalls, dwalls, 0.0, 0.0, 0.0), SAND, block_type='brick', collision_reward = -1)

    # Build reward block in the corner
    model.add_block( (n-(wr/2+dwalls/2), bot_height/2.0, -n+(wr/2+dwalls/2), wr, bot_height/3.0, wr, 0.0, 0.0, 0.0),
                     texture=REWARD, block_type='reward', collision_reward = 1, visible_reward=visible_reward)
    # Build robot block, set initial height to bot_heigh/2 + small offset to avoid ground collision
    model.add_block( (0, bot_height/2.0+0.1, 0, 2*bot_radius, bot_height, 2*bot_radius, 0.0, 0.0, 0.0),
                     texture=BOT, block_type='robot')
    # add starting areas (the height=0 of block does not matter here, only area of (hwalls-2*dwalls)^2)
    model.add_block( (0, bot_height/2.0+0.1, (wwalls-2*dwalls)/4, wwalls-2*dwalls, 0.1, (wwalls-2*dwalls)/2, 0.0, 0.0, 0.0),
                     texture=START, block_type='start')
    model.add_block( ( -(wwalls-2*dwalls)/4, bot_height/2.0+0.1, -(wwalls-2*dwalls)/4, (wwalls-2*dwalls)/2, 0.1, (wwalls-2*dwalls)/2, 0.0, 0.0, 0.0),
                     texture=START, block_type='start')


    return texture_paths, world_info

