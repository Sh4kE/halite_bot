"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Sh4kE")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")


def all_planets_owned():
    for planet in game.map.all_planets():
        if not planet.is_owned():
            return False
    return True


def move_to_planet(planet):
    # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
    if ship.can_dock(planet):
        # We add the command by appending it to the command_queue
        command_queue.append(ship.dock(planet))
    else:
        # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
        # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
        # We run this navigate command each turn until we arrive to get the latest move.
        # Here we move at half our maximum speed to better control the ships
        # In order to execute faster we also choose to ignore ship collision calculations during navigation.
        # This will mean that you have a higher probability of crashing into ships, but it also means you will
        # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
        # wish to turn that option off.
        navigate_command = ship.navigate(
            ship.closest_point_to(planet),
            game_map,
            speed=int(hlt.constants.MAX_SPEED))
        # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
        # or we are trapped (or we reached our destination!), navigate_command will return null;
        # don't fret though, we can run the command again the next turn)
        if navigate_command:
            planets_moving_to.append(planet)
            command_queue.append(navigate_command)


def attack_one_of_docked_ships(planet):
    for enemy_ship in planet.all_docked_ships():
        if enemy_ship not in ships_to_attack:
            ships_to_attack.append(enemy_ship)
            attack_entity(ship)
            break


def attack_entity(entity):
    navigate_command = ship.navigate(
        ship.closest_point_to(entity, 0),
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=False)
    if navigate_command:
        command_queue.append(navigate_command)


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    planets_moving_to = []
    ships_to_attack = []
    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        planets_by_distance = [entities_by_distance[distance][0] for distance in sorted(entities_by_distance)
                               if isinstance(entities_by_distance[distance][0], hlt.entity.Planet)]

        for planet in planets_by_distance:
            if all_planets_owned():
                # attack ships of the nearest planet I'm not the owner of
                not_my_planets_by_distance = [planet for planet in planets_by_distance
                                              if planet.owner != game.map.get_me()]

                if len(not_my_planets_by_distance) > 0:
                    attack_one_of_docked_ships(not_my_planets_by_distance[0])
                    break

            if planet.is_owned() or planet in planets_moving_to:
                # Otherwise skip this planet
                continue

            move_to_planet(planet)
            break

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END

