cmake_minimum_required(VERSION 3.23)
project(crs C)

set(CMAKE_C_STANDARD 11)

include_directories(.)

add_executable(crs
        client.c
        client.h
        commands.c
        commands.h
        const.h
        main.c
        util.c
        util.h
        validate.c
        validate.h)
