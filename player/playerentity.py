import logic
from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.readable import Readable
from player.inventory import Inventory
from movement.scene import Scene
from console.colors import white, reset, red, green

import re
from difflib import SequenceMatcher


# Check how similar two strings are
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Filter through a list of items and find all that either match or are similar to
# the string query. Return a dictionary list of all matching items.
def get_match(args, item_list):
    items = []
    for item in item_list:
        arg_split = sum([re.split(r'[^\w ]', x) for x in args.split()], [])
        name_split = sum([re.split(r'[^\w ]', x) for x in item.get_name().lower().split()], [])
        for arg in arg_split:
            if any(similar(arg, x) > 0.75 for x in name_split):
                items.append(item)
    return list(dict.fromkeys(items))


def get_containers(items):
    return [item for item in items if isinstance(item, Container)]


def add_item(matches, iterating, container):
    for match in matches:
        if not isinstance(match, Container):
            if not container.get_contents().full():
                container.get_contents().get_items().append(match)
                iterating.remove(match)
                logic.global_console.wrap(
                    f"You put {white}{match.get_name()}{reset} into {white}{container.get_name()}{reset}. "
                    f"Now it deals {container.get_damage()} damage.")
            else:
                logic.global_console.wrap(
                    f"The {white}{container.get_name()}{reset} is too full to fit {white}{match.get_name()}{reset}")
        else:
            print("You cannot put a container inside a container.")


def take(matches, iterating, player):
    for match in matches:
        if match.get_take()[0] == "true" and not isinstance(match, Enemy):
            if not player.get_inventory().full():
                player.get_inventory().get_items().append(match)
                iterating.remove(match)
                if match.get_take()[1] is not None:
                    print(match.get_take()[1])
                logic.global_console.wrap(f"You picked up {white}{match.get_name()}{reset}.")
            else:
                print("Your inventory is too full to pick that up!")
        else:
            if match.get_take()[0] == "consequence":
                player.change_health(-match.get_damage())
                print(f'{match.get_take()[1]} -{match.get_damage()} HP')
            else:
                logic.global_console.wrap(f"You can't pick up a {white}{match.get_name()}{reset}!")


class PlayerEntity:
    # Initialise the health, inventory and current scene of the player
    max_health = 0
    health = 0
    inventory: Inventory
    current_scene: Scene
    combat: bool = False

    # Define the constructor to be called when a new Player object is created
    def __init__(self, health, inventory, current_scene):
        self.max_health = health
        self.health = health
        self.inventory = inventory
        self.current_scene = current_scene

    # Return the health of the player
    def get_health(self):
        return self.health

    # Change the health of the player by an amount passed in parameters
    def change_health(self, amount):
        self.health += int(amount)
        if self.health > self.max_health:
            self.health = self.max_health

    def kill(self):
        self.change_health(-self.max_health)

    # Get the current scene the player is in
    def get_current_scene(self):
        return self.current_scene

    # Set the current scene the player is in
    def set_current_scene(self, scene):
        self.current_scene = scene

    # Get the coordinate Z level (height) of the player
    def get_z(self):
        return self.current_scene.get_coordinate().z

    # Return a list of all items in the player's inventory
    def get_inventory(self):
        return self.inventory

    # Return a list of all weapons in the player's inventory
    def get_weapons(self):
        return [weapon for weapon in self.inventory.get_items() if not isinstance(weapon, Food)]

    # Get a queried Container object from the player's inventory
    def get_container(self, args):
        inventory_objects = get_match(args, self.inventory.get_items())
        scene_objects = get_match(args, self.get_current_scene().get_items())
        for obj in inventory_objects:
            if isinstance(obj, Container):
                return obj
        for obj in scene_objects:
            if isinstance(obj, Container):
                return obj

    # Get a queried Enemy object from the player's current scene
    def get_enemy(self, args):
        scene_objects = get_match(args, self.get_current_scene().get_items())
        for obj in scene_objects:
            if isinstance(obj, Enemy):
                return obj

    # Add an item from the player's inventory to a container in the player's inventory
    def container_add(self, args: str, container: Container):
        # If no item or container was specified
        if container is None:
            print("You must have the container in your inventory.")
            print("Syntax: put [item] in [container]")
            return
        if args == "":
            print("Specify what you want to add to that container.")
            print("Syntax: put [item] in [container]")
            return
        # Get a list of items in the player's inventory that match the player's query
        inv_matches = get_match(args.replace(container.get_name().lower(), ""), self.inventory.get_items())
        scene_matches = get_match(args.replace(container.get_name().lower(), ""), self.get_current_scene().get_items())
        # For each item found, add it to the container if it is light enough and not a container itself
        if len(inv_matches) > 0:
            add_item(inv_matches, self.inventory.get_items(), container)
        elif len(scene_matches) > 0:
            add_item(scene_matches, self.get_current_scene().get_items(), container)
        else:
            print("You do not have that.")
            return

    # Remove an item from a container in the player's inventory
    def container_remove(self, args: str, container: Container):
        # If no item or container was specified
        if container is None:
            print("You must have the container in your inventory.")
            print("Syntax: take [item] out of [container]")
            return
        if args == "":
            print("Specify what you want to take out of that container.")
            print("Syntax: take [item] out of [container]")
            return
        # Get a list of items in the container that match the player's query
        matches = get_match(args, container.get_contents().get_items())
        if len(matches) < 1:
            logic.global_console.wrap(f"That item isn't in the {white}{container.get_name()}{reset}.")
            return
        # For each item found, remove it from the container and add to inventory
        for match in matches:
            container.get_contents().get_items().remove(match)
            self.inventory.get_items().append(match)
            logic.global_console.wrap(
                f"You took {white}{match.get_name()}{reset} out of {white}{container.get_name()}{reset}. "
                f"Now it deals {container.get_damage()} damage.")

    # Pick up an item in the player's scene
    def pick_up(self, args: str):
        # If no item was specified
        if args == "":
            print("What do you want to pick up?")
            print("Syntax: take [item]")
            return
        # Get a list of items in the player's current scene that match the player's query
        inv_matches = get_match(args, self.get_current_scene().get_items())
        scene_matches = []
        for container in get_containers(self.get_current_scene().get_items()):
            scene_matches = [*scene_matches, *get_match(args, container.get_contents().get_items())]
        if len(inv_matches) > 0:
            take(inv_matches, self.get_current_scene().get_items(), self)
        elif len(scene_matches) > 0:
            for container in get_containers(self.get_current_scene().get_items()):
                matches = get_match(args, container.get_contents().get_items())
                if len(matches) > 0:
                    take(matches, container.get_contents().get_items(), self)
        else:
            print(f"Theres no \"{args}\" here.")
            return
        # If the item can be taken and is not an enemy, then add it
        # to the player's inventory and remove it from the scene

    # Remove/drop an item from player's inventory
    def drop(self, args: str):
        # If no item was specified
        if args == "":
            print("What do you want to drop?")
            print("Syntax: drop [item]")
            return
        # Get a list of items in the player's inventory that match the player's query
        inv_matches = get_match(args, self.get_inventory().get_items())
        inv_container_matches = []
        for container in get_containers(self.get_inventory().get_items()):
            inv_container_matches = [*inv_container_matches, *get_match(args, container.get_contents().get_items())]
        if len(inv_matches) > 0:
            for match in inv_matches:
                self.inventory.get_items().remove(match)
                self.get_current_scene().get_items().append(match)
                logic.global_console.wrap(f"Dropped {white}{match.get_name()}{reset}.")
        elif len(inv_container_matches) > 0:
            for container in get_containers(self.get_inventory().get_items()):
                for match in inv_container_matches:
                    if match in container.get_contents().get_items():
                        container.get_contents().get_items().remove(match)
                        self.get_current_scene().get_items().append(match)
                        logic.global_console.wrap(
                            f"Dropped {white}{match.get_name()}{reset} from {white}{container.get_name()}{reset}.")
        else:
            print(f"Theres no \"{args}\" here.")
            return

    # Eat an item in the player's inventory
    def eat(self, args):
        # If no item was specified
        if args == "":
            print("Specify what you want to eat.")
            print("Syntax: eat [item]")
            return
        # Get a list of items in the player's inventory that match the player's query
        matches = get_match(args, self.inventory.get_items())
        if len(matches) < 1:
            print(f"You don't have that in your inventory.")
            return
        # For each match in the inventory, add saturation of the food to the player's health
        # and remove it from their inventory, as long it is an actual food and edible.
        for match in matches:
            if match.get_take()[0] == "true" and isinstance(match, Food):
                self.change_health(match.get_saturation())
                self.inventory.get_items().remove(match)
                if match.get_take()[1] is not None:
                    print(match.get_take()[1])
                logic.global_console.wrap(
                    f"You ate {white}{match.get_name()}{reset}, and gained {match.get_saturation()} HP."
                    f"\nYou are now on {self.health} HP.")
            else:
                logic.global_console.wrap(f"You cannot eat a {white}{match.get_name()}{reset}!")

    # Read an item in the player's inventory
    def read(self, args):
        # If no item was specified
        if args == "":
            print("Specify what you want to read.")
            print("Syntax: read [item]")
            return
        # Get a list of items in the player's inventory that match the player's query
        matches = [*get_match(args, self.inventory.get_items()), *get_match(args, self.get_current_scene().get_items())]
        if len(matches) < 1:
            print(f"Item not found.")
            return
        # For each match in the inventory, read its text
        for match in matches:
            if match.get_take()[0] == "true" and isinstance(match, Readable):
                logic.global_console.wrap(f"The {white}{match.get_name()}{reset} reads:"
                      f"\n{match.text}")
            else:
                logic.global_console.wrap(f"You cannot read that {white}{match.get_name()}{reset}!")

    # Swing a weapon at an enemy, dealing it damage
    def swing(self, args, enemy: Enemy):
        # If no weapon or enemy was specified
        if enemy is None:
            print("No enemy found.")
            return
        if args == "":
            print("Specify what you want to attack.")
            print("Syntax: attack [enemy] with [weapon]")
            return
        # Get a list of all items in the player's inventory that match the query
        matches = get_match(args, self.get_weapons())
        if len(matches) < 1:
            print(f"You don't have that.")
            return
        # If the enemy is alive, attack it and change the player's health depending on
        # the enemy's strength. If it is dead, do not attack it.
        for match in matches:
            if enemy.is_alive():
                enemy.change_health(-match.get_damage())
                logic.reset_timer()
                logic.global_console.wrap(
                    f"You attacked the {white}{enemy.get_name()}{reset} with a {white}{match.get_name()}{reset} for {match.get_damage()} damage.")
                if enemy.is_alive():
                    self.change_health(-enemy.get_damage())
                    logic.global_console.wrap(
                        f"It swings back at you, dealing {enemy.get_damage()} damage to you. Your health: {self.get_health()}"
                        f"\nThe {white}{enemy.get_name()}{reset} is now on {enemy.get_health()} HP.")
                    if not self.combat:
                        self.combat = True
                        logic.global_console.wrap(f"{red}You are now in combat.")
                else:
                    dropped = []
                    enemy_inventory = [x for x in enemy.get_inventory().get_items()]
                    for item in enemy_inventory:
                        if item.get_take()[0] == "true":
                            self.get_current_scene().get_items().append(item)
                            enemy.get_inventory().get_items().remove(item)
                            dropped.append(item.get_name())
                    logic.global_console.wrap(f"The {white}{enemy.get_name()}{reset} is now dead.")
                    print(
                        f'It dropped a {f", a ".join(dropped)}.') if len(
                        dropped) > 0 else print("", end='')
                    enemy.set_name(f"Dead {enemy.get_name()}")
                    if self.combat:
                        logic.global_console.wrap(f"{green}You are no longer in combat.")
                    self.combat = False
            else:
                logic.global_console.wrap(f"That {white}{enemy.get_name()}{reset} is already dead.")
