# ---------------------------------------------------------------------------------------------------------------------
#
# Copyright (C) Microsoft Corporation.  All rights reserved.
#
# Module Name:
#
#   CMakeLists.txt
#
# Abstract:
#
#   CMake build file.
#
# ---------------------------------------------------------------------------------------------------------------------

set(TARGET_NAME multirotor_api)

add_library(
    ${TARGET_NAME}
    STATIC
    mavlink_api.cpp
    manual_controller_api.cpp
    matlab_controller_api.cpp
    multirotor_api_base.cpp
    simple_flight_api.cpp
    vtolfw_api_base.cpp
    arducopter_api.cpp
)

set_target_properties(${TARGET_NAME} PROPERTIES
    POSITION_INDEPENDENT_CODE ON
    COMPILE_PDB_NAME ${TARGET_NAME}
    COMPILE_PDB_OUTPUT_DIR ${CMAKE_BINARY_DIR}
)

add_dependencies(${TARGET_NAME} core_sim)
add_dependencies(${TARGET_NAME} mavlinkcom)
add_dependencies(${TARGET_NAME} nng-external)

# Set up nng for linking
target_link_directories(${TARGET_NAME} PRIVATE ${NNG_LIB_DIR} ${OPENSSL_LIB_DIR})
target_compile_definitions(${TARGET_NAME} PRIVATE NNG_STATIC_LIB=ON)

target_include_directories(
    ${TARGET_NAME}
    PUBLIC
        $<INSTALL_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
        $<INSTALL_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../include>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${EIGEN_INCLUDE_DIR}
        ${JSON_INCLUDE_DIR}
        ${NNG_INCLUDE_DIR}
        ${MSGPACK_INCLUDE_DIR}
)

if(WIN32)
    target_link_libraries(
        ${TARGET_NAME}
        PRIVATE
            core_sim
            mavlinkcom
            lvmon
            nng
            ws2_32  # req by nng on Win
            mswsock  # req by nng on Win
            advapi32  # req by nng on Win
    )
else()
    target_link_libraries(
        ${TARGET_NAME}
        PRIVATE
        core_sim
        mavlinkcom
        lvmon
        nng
    )
endif()

add_custom_command(TARGET ${TARGET_NAME}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "Packaging [${TARGET_NAME}] build outputs to ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/$<IF:$<CONFIG:Release>,Release,Debug>"
    COMMAND ${CMAKE_COMMAND} -E copy_directory $<TARGET_FILE_DIR:${TARGET_NAME}> ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/$<IF:$<CONFIG:Release>,Release,Debug>
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/../include ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/include
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/../../include/common ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/include/common
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/$<IF:$<CONFIG:Release>,Release,Debug>/CMakeFiles
    COMMAND ${CMAKE_COMMAND} -E remove -f ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/$<IF:$<CONFIG:Release>,Release,Debug>/cmake_install.cmake
    COMMAND ${CMAKE_COMMAND} -E remove -f ${UE_PLUGIN_SIMLIBS_DIR}/${TARGET_NAME}/$<IF:$<CONFIG:Release>,Release,Debug>/CTestTestfile.cmake

    # Also copy physics lib message headers to Matlab physics S-function folder for building in Matlab:
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/../include/message ${CMAKE_CURRENT_SOURCE_DIR}/../matlab_sfunc/message
)
