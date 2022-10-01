# Dynamic connect-3

Assignment 1 for ECSE526 AI course at McGill University

## Player vs AI

To play against the agent, use the following command :
```bash
python3 against_player.py 
```

## AI vs AI on server

To battle the AI against another on the tournament server, use the command :
```bash
python3 against_server.py --game_id <game_id> --color <white or black> 
```

By default, you'll play on the 5x4 board. To play on the 7x6 add the option :
```bash
python3 against_server.py --game_id <game_id> --color <white or black> --size_grid 2
```