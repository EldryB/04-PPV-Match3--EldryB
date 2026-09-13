"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer
from src.Tile import Tile

import settings


class PlayState(BaseState):

    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        self.dragged_tile:Tile = None
        self.start_i:int = 0
        self.start_j:int = 0

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        if self.dragged_tile is not None:
            pos_x, pos_y = pygame.mouse.get_pos()
            
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            
            self.dragged_tile.x = pos_x - self.board.x - (settings.TILE_SIZE // 2)

            self.dragged_tile.y = pos_y - self.board.y - (settings.TILE_SIZE // 2)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)



        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click":
            if input_data.pressed:
                pos_x, pos_y = input_data.position
                pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE

                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    self.dragged_tile = self.board.tiles[i][j]
                    self.start_i = i
                    self.start_j = j

            else:
                if self.dragged_tile is not None:
                    pos_x, pos_y = input_data.position
                    pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                    pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT

                    i = (pos_y - self.board.y) // settings.TILE_SIZE
                    j = (pos_x - self.board.x) // settings.TILE_SIZE

                    di = abs(i - self.start_i)
                    dj = abs(j - self.start_j)

                    tile1 = self.dragged_tile

                    if di == 0 and dj == 0:#Click sobre un tale
                        if getattr(tile1, 'powerup', None) is not None:

                            self.active = False
                            self.dragged_tile = None
                            

                            explosion = [tile1] + self.board.get_powerup_effect(tile1)
                            self.board.matches.append(explosion)
                            

                            settings.SOUNDS["match"].stop()
                            settings.SOUNDS["match"].play()

                            self.board.remove_matches()
                            falling_tiles = self.board.get_falling_tiles()
                            
                            Timer.tween(
                                0.25,
                                falling_tiles,
                                on_finish=lambda: self._calculate_matches([item[0] for item in falling_tiles])
                            )
                        else:
                            self.dragged_tile = None
                        return
                    
                    elif 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH and di <= 1 and dj <= 1 and di != dj:
                        self.active = False
                        tile2 = self.board.tiles[i][j]
                        
                        (
                            self.board.tiles[self.start_i][self.start_j],
                            self.board.tiles[i][j],
                        ) = (
                            self.board.tiles[i][j],
                            self.board.tiles[self.start_i][self.start_j],
                        )
                        tile1.i, tile1.j, tile2.i, tile2.j = tile2.i, tile2.j, tile1.i, tile1.j
                        
                        matches = self.board.calculate_matches_for([tile1, tile2])
                        
                        original_x = self.start_j * settings.TILE_SIZE
                        original_y = self.start_i * settings.TILE_SIZE

                        if matches is None:
                            (
                                self.board.tiles[self.start_i][self.start_j],
                                self.board.tiles[i][j],
                            ) = (
                                self.board.tiles[i][j],
                                self.board.tiles[self.start_i][self.start_j],
                            )
                            tile1.i, tile1.j, tile2.i, tile2.j = tile2.i, tile2.j, tile1.i, tile1.j
                        
                            self.dragged_tile = None
                            def restore_control():
                                self.active = True
                                
                            Timer.tween(
                                0.25,
                                [(tile1, {"x": original_x, "y": original_y})],
                                on_finish=restore_control
                            )

                        
                        else:
                            
                            self.dragged_tile = None
                            
                            def process_valid_move():
                                self._calculate_matches([tile1, tile2], epicenter_i=i, epicenter_j=j)


                            Timer.tween(
                                0.25,
                                [
                                    (tile1, {"x": tile2.x, "y": tile2.y}),
                                    (tile2, {"x": original_x, "y": original_y}),
                                ],
                                on_finish=process_valid_move
                            )
                            
                    else:

                        tile1 = self.dragged_tile
                        self.dragged_tile = None 
                        
                        original_x = self.start_j * settings.TILE_SIZE
                        original_y = self.start_i * settings.TILE_SIZE
                        
                        self.active = False
            
                        def restore_control():
                            self.active = True
            
                        Timer.tween(
                            0.25, 
                            [(tile1, {"x": original_x, "y": original_y})],

                            on_finish=restore_control
                        )
        

    def _calculate_matches(self, tiles: List, epicenter_i: int = -1, epicenter_j: int = -1) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:

            while (not self.board.has_possible_moves() and not self.board.check_powerup()):
                print("Tablero Reordenado") #Debug
                self.board._initialize_tiles()

            self.active = True
            return

        for match in matches:
            extra_explosions = []

            for tile in match:
                if getattr(tile, 'powerup', None) is not None:
                    extra_explosions.extend(self.board.get_powerup_effect(tile))
            
            if len(extra_explosions) > 0:
                self.board.matches.append(extra_explosions)
                self.score += len(extra_explosions) * 50 #Puntaje extra por explosion
            
            if len(match) >= 4:
                p_type = "bomb" if len(match) >= 5 else "line"
                
                spawn_tile = match[0]
                
                for t in match:
                    if t.i == epicenter_i and t.j == epicenter_j:
                        spawn_tile = t
                        break
                        
                spawn_tile.powerup = p_type
                #Sacar el tile de match para que despues no sea destruida
                match.remove(spawn_tile)

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )
