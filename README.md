# Manolonga server
Python backend server for [Manolonga](https://github.com/TakFog/manolonga) game.

# Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
   - [`SERVER_PORT`](#server_port)
   - [`SERVER_HOST`](#server_host)
   - [`GAME_ID_LENGTH`](#game_id_length)
   - [`DEBUG`](#debug)
3. [Endpoints](#endpoints)
   - [Create a Game](#create-a-game)
   - [Generate Game Layout](#generate-game-layout)
   - [Update Game State](#update-game-state)
   - [Clear Game State](#clear-game-state)
4. [Background Cleanup](#background-cleanup)

## Overview

This document provides an overview of the endpoints available in the Flask application. The application allows for the 
creation and management of game states, including the generation of game layouts and the updating of player states.

## Environment Variables

The Flask application uses several environment variables to configure its behavior. This document provides an overview 
of these environment variables and their default values.

### `SERVER_PORT`

- **Description:** Specifies the port on which the Flask application will run.
- **Default Value:** `8080`
- **Example Usage:** `SERVER_PORT=5000`

### `SERVER_HOST`

- **Description:** Specifies the the network interface on which the server should listen for incoming requests.
- **Default Value:** `0.0.0.0`
- **Example Usage:** `SERVER_HOST=127.0.0.1`

### `GAME_ID_LENGTH`

- **Description:** Specifies the length of the game ID generated for each new game.
- **Default Value:** `4`
- **Example Usage:** `GAME_ID_LENGTH=6`

### `DEBUG`

- **Description:** Enables or disables debug mode for the Flask application. 
Set to `1` to enable debug mode, `0` to disable it.
- **Default Value:** `0`
- **Example Usage:** `DEBUG=1`

## Endpoints

### Create a Game

- **Endpoint:** `/createGame`
- **Method:** `GET`
- **Description:** Creates a new game and returns a unique game ID.
- **Response:**
  - `200 OK`: Returns a JSON object containing the `gameid`.
  - **Example Response:**
    ```json
    {
      "gameid": "ABCD"
    }
    ```

### Generate Game Layout

- **Endpoint:** `/<string:gameid>/init`
- **Method:** `POST`
- **Description:** Generates a game layout for the specified game ID. The layout includes open exits, monster spawn location, and child spawn location.
- **Request Body:**
  - `numExits` (integer): Total number of exits.
  - `numOpenExits` (integer): Number of open exits.
  - `numMonsterSpawns` (integer): Number of monster spawn points.
  - `numChildSpawns` (integer): Number of child spawn points.
  - **Example Request:**
    ```json
    {
      "numExits": 4,
      "numOpenExits": 2,
      "numMonsterSpawns": 10,
      "numChildSpawns": 5
    }
    ```
- **Response:**
  - `200 OK`: Returns a JSON object containing the game layout.
  - **Example Response:**
    ```json
    {
      "openExits": [1, 3, 7, 9],
      "monsterSpawn": 0,
      "childSpawn": 4
    }
    ```

### Update Game State

- **Endpoint:** `/<string:gameid>/updateState/<string:player_id>/<int:round_id>`
- **Method:** `POST`
- **Description:** Updates the game state for a given player and round.
- **Request Body:** JSON object representing the state to be updated.
  - **Example Request:**
    ```json
    {
      "actionType": 1,
      "positionsPath": [
        {"x": -1.0, "y": 0.0, "z": 0.0},
        {"x":  0.0, "y": 0.0, "z": 0.0}
      ]
    }
    ```
- **Response:**
  - `200 OK`: Returns a JSON object containing the updated state for the round.
  - **Example Response:**
    ```json
    {
      "Child": {
        "actionType": 1,
        "positionsPath": [
          {"x": -1.0, "y": 0.0, "z": 0.0},
          {"x":  0.0, "y": 0.0, "z": 0.0}
        ]
      },
      "Monster": {
        "actionType": 3,
        "positionsPath": [
          {"x": -7.5, "y": -4.06874942779541  , "z": 0.0},
          {"x": -7.0, "y": -3.487499713897705 , "z": 0.0},
          {"x": -6.5, "y": -2.906249761581421 , "z": 0.0},
          {"x": -6.0, "y": -2.3249998092651367, "z": 0.0}
        ]
      },
      "hasChild": true,
      "hasMonster": true
    }
    ```

### Clear Game State

- **Endpoint:** `/<string:gameid>/clear`
- **Method:** `GET`
- **Description:** Clears the game state for the specified game ID.
- **Response:**
  - `200 OK`: Returns a message indicating that the state has been cleared.
  - **Example Response:**
    ```text
    State cleared
    ```

## Background Cleanup

A background thread runs every hour to clean up old games that have not been updated in the last 24 hours. 
This helps to manage memory usage and keep the system running efficiently.
