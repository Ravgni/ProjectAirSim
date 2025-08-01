"""
Copyright (C) Microsoft Corporation. All rights reserved.

Demo client script for combined Project AirSim ROS2 Bridge node and mission
script.

From a Project AirSim virtual Python environment, run this script and specify:
1. The IP address of the Project AirSim server with the "--ipaddress" flag if
   the server is not running on the local machine, and
2. The path to the simulation configuration files with the "--simconfigpath" flag
   (e.g., "../../../client/python/example_user_scripts/sim_config".)
"""
import argparse
import asyncio
from time import time
import traceback


import rclpy

import projectairsim
from projectairsim.utils import projectairsim_log
from projectairsim_ros2 import ROS2Node
from projectairsim_rosbridge import ProjectAirSimROSBridge


client = None  # Project AirSim client


async def do_mission(client, world):
    # Create a drone object to interact with a Drone in the loaded Project AirSim world
    drone = projectairsim.Drone(client, world, "Drone1")

    # ------------------------------------------------------------------------------

    # Set the drone to be ready to fly
    drone.enable_api_control()
    drone.arm()

    # ------------------------------------------------------------------------------

    while True:
        # Fly the drone around the scene
        projectairsim_log().info("Move up")
        move_task = await drone.move_by_velocity_async(
            v_north=0.0, v_east=0.0, v_down=-3.0, duration=4.0
        )
        await move_task

        projectairsim_log().info("Move north")
        move_task = await drone.move_by_velocity_async(
            v_north=4.0, v_east=0.0, v_down=0.0, duration=12.0
        )
        await move_task

        projectairsim_log().info("Move north-east")
        move_task = await drone.move_by_velocity_async(
            v_north=4.0, v_east=4.0, v_down=0.0, duration=8.0
        )
        await move_task

        projectairsim_log().info("Move north")
        move_task = await drone.move_by_velocity_async(
            v_north=4.0, v_east=0.0, v_down=0.0, duration=3.0
        )
        await move_task

        projectairsim_log().info("Move down")
        move_task = await drone.move_by_velocity_async(
            v_north=0.0, v_east=0.0, v_down=3.0, duration=4.0
        )
        await move_task

        await asyncio.sleep(2)

        projectairsim_log().info("Move up")
        move_task = await drone.move_by_velocity_async(
            v_north=0.0, v_east=0.0, v_down=-3.0, duration=2.0
        )
        await move_task

        projectairsim_log().info("Move south")
        move_task = await drone.move_by_velocity_async(
            v_north=-4.0, v_east=0.0, v_down=0.0, duration=3.0
        )
        await move_task

        projectairsim_log().info("Move south-west")
        move_task = await drone.move_by_velocity_async(
            v_north=-4.0, v_east=-4.0, v_down=0.0, duration=8.0
        )
        await move_task

        projectairsim_log().info("Move south")
        move_task = await drone.move_by_velocity_async(
            v_north=-4.0, v_east=0.0, v_down=0.0, duration=12.0
        )
        await move_task

        projectairsim_log().info("Move down")
        move_task = await drone.move_by_velocity_async(
            v_north=0.0, v_east=0.0, v_down=3.0, duration=4.0
        )
        await move_task

        projectairsim_log().info("Go home")
        gohome_task = await drone.go_home_async()
        await gohome_task

        projectairsim_log().info("Land")
        gohome_task = await drone.land_async()
        await gohome_task

        await asyncio.sleep(2)


async def main(ros_node, client, world):
    # Launch mission task
    mission_task = asyncio.create_task(do_mission(client, world))

    # IMPORTANT: Process ROS messages until ROS is shutdown
    try:
        while ros_node.spin_once():
            await asyncio.sleep(0.001)
    except KeyboardInterrupt:
        pass
    except:
        print(f"caught exception: {traceback.format_exc()}")
        pass

    # Shutdown mission task
    projectairsim_log().info("Stopping mission script")
    try:
        while not mission_task.done():
            mission_task.cancel()
            await asyncio.wait({mission_task}, timeout=1)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Robotic Operating System (ROS) node that bridges Project AirSim and ROS2."
    )
    parser.add_argument(
        "--address",
        help=("the IP address of the host running Project AirSim"),
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "--nodename",
        help=(
            'the name for this ROS node; if not given, the node is given an anonymous name starting with "projectairsim"'
        ),
        type=str,
        default="",
    )
    parser.add_argument(
        "--simconfigpath",
        help=("the directory containing Project AirSim config files"),
        type=str,
        default="../../../client/python/example_user_scripts/sim_config",
    )
    parser.add_argument(
        "--topicsport",
        help=(
            "the TCP/IP port of Project AirSim's topic pub-sub client connection "
            '(see the Project AirSim command line switch "-topicsport")'
        ),
        type=int,
        default=8989,
    )
    parser.add_argument(
        "--servicesport",
        help=(
            "the TCP/IP port of Project AirSim's services client connection "
            '(see the Project AirSim command line switch "-servicessport")'
        ),
        type=int,
        default=8990,
    )

    # Parse command-line
    args = parser.parse_args(args=rclpy.utilities.remove_ros_args()[1:])

    # Initialize ROS and start our node
    rclpy.init()
    if args.nodename == "":
        node_name = "projectairsim"
        anonymous_node_name = True
    else:
        node_name = args.nodename
        anonymous_node_name = False

    # Create client to Project AirSim
    client = projectairsim.ProjectAirSimClient(
        address=args.address,
        port_topics=args.topicsport,
        port_services=args.servicesport,
    )
    client.connect()

    # Load scene
    world = projectairsim.World(
        client,
        "scene_drone_sensors.jsonc",
        sim_config_path=args.simconfigpath,
        delay_after_load_sec=2,
    )

    # Create ROS wrapper and start ROS operations
    projectairsim_log().info(
        f'Starting ROS node "{node_name}"{" anonymized" if anonymous_node_name else ""}'
    )
    ros_node = ROS2Node(name=node_name, anonymous=anonymous_node_name)
    if anonymous_node_name:
        projectairsim_log().info(f'ROS node name is "{ros_node.name}"')
    projectairsim_ros_bridge = ProjectAirSimROSBridge(
        ros_node=ros_node, client=client, sim_config_path=args.simconfigpath
    )

    # Start drone movement and ROS node
    try:
        asyncio.run(main(ros_node, client, world))
    except KeyboardInterrupt:
        pass

    # Shutdown ROS
    if ros_node.ros_is_running:
        projectairsim_log().info("Shutting down ROS")
        rclpy.try_shutdown()

    # Close the client
    if client is not None:
        client.disconnect()
        del client

    projectairsim_log().info("Shutdown complete.")
