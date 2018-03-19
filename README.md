# bra-ket-wolf

An implementation of Quantum Werewolf by [Vincent Verhoeven](verhoevenv@gmail.com)

Quantum Werewolf is a variant on the well-known party game Werewolf (AKA Mafia). This variant was designed by Steven Irrgang. The main idea is that players don't have one role given tot them but have all roles at the same time in a kind of quantum superposition. Full rules are available on http://puzzle.cisra.com.au/2008/quantumwerewolf.html

This implementation is probably not the fastest possible. Because all possible game states are generated (a combinatorial explosion), it is at the moment probably impossible to play beyond 10 or 11 players.

The current implementation has the villager, werewolf and seer roles.

## TODO
* move this list to the issue tracker :D
* improve speed (Monte-Carlo simulations, some improvements in game state generation)
* add more roles
  * allow forced N0 negative vision for seer for game balance (hah)
* generate a given small number of universes instead of percentage of all universes
* Usability
  * better parsing (like player names)
  * 'state' command could give some more information about what it's displaying
  * feedback when entering state-changing commands like 'attack' or 'kill'
  * undo command
  * warnings on overwriting save files

## Requirements
Python 2.6 or higher.

## License
GPL v3 licensed.

## Documentation
### General
The general idea of what this software will help you do is administrate a silly amount of werewolf games (_universes_) in parallel - we'll adhere to the many-worlds-theory of quantum mechanics. All possible werewolf games are simulated at the same time and tested for validity. It is, for example, not possible for werewolf player A to kill someone in turn 1 and then be seen as 'not evil' in turn 2. Validity is backed up by '_evidence_'. For example, someone dying on a certain turn is evidence: if player A died on turn 2 by public lynching, it is not possible for him to have died on turn 1 by a werewolf kill. So all universes with werewolves attacking player A on turn 1 '_collapse_' : they are invalid and will be discarded.
Evidence can also be conditional, like in the seer example a few lines back. If player B has a 'not evil' vision about player A (visions are evidence), it means he is either a Seer and thus player A is not a wolf, or he is not a Seer, which means his visions are random, and thus it says nothing about player A. If player A IS a wolf, it means player B CANNOT be a seer: that would be contradictory. We don't know what information will be revealed first (A being wolf or B being seer), but either might change the state of the other. Wheee!

Another important concept. In regular werewolf, people have a secret role. In quantum werewolf, people have a _secret player number_, and the mapping from player number to roles is public knowledge. All players have all roles, and are able to carry out all actions associated with those roles.

### UI
The frontend for the game is a command-line based text UI, started with 'python main.py'. You can get a list of commands by using the 'help' command. The help command is also useful to get a brief reminder of what a command does, with something like
```
help players
```
I'll walk you through the start of a game to give an idea of what the commands do.

### Players
No game without players, so first, we need to enter our list of players. This list should probably not be too big, I think about 15 players would be the max, depending on hardware.
```
players Alice,Bob,Remus,David
```
Take care not to use spaces in the list!

### Roles
The game will provide a distribution of roles for the number of players entered. I have no idea about game balance, I just did something there. To see the current role distribution:
```
roles
```
You can alter the role distribution. If you wanted a game with no seer and 2 werewolves, you'd do
```
roles Villager 2, Wolf 2
```
but I'll keep with the default of Villager 2, Seer 1, Wolf 1 for our 4 player demonstration.

### Breaking the symmetry
It's possible to randomly throw away a percentage of the generated universes, to break the symmetry a bit. By default, the program will create all possible combinations of universes. We'll keep it a bit lower to keep some randomness in the game.
```
keepfraction 0.5
```
The command above will keep half of the generated universes.

### Starting the game
That's it for the preface, we can now start playing! That's actually easy:
```
start
```
Depending on the number of players, this might take a while. It will generate a lot of universes.

### Displaying state
When it has finished calculating (you won't have to wait with just 4 players), you can see the state of the game with the 'state' command:
```
state
```
This will display a few bits of data, Python-style.
First is the time. The game will start at N0, which means 'the night before the actual game starts'. It'll go to D1, N1, D2, N2, ..
Then is a map of players to their role distribution. For each role, this is all universes where they have the role, divided by the number of universes.
Third is a map of players to their deadness, if that's even a word. It's the fraction of universes the player is dead in, divided by the total number of universes.
Last is a number with the total number of non-collapsed (so internally consistent) universes. Probably not that useful, but fun to brag about.

A better way to display this data is with
```
namedtable
```
This is mainly for the benefit of the game master and the post-game discussion. For your players, you would use
```
table
```
because this hides the names. Remember, players have a player number which is secret! Oh, don't forget to hand your players their player number at the start of the game via private message or something - you can find the info via namedtable.

### Saving and loading
We already covered most of the commands! Next, we want to take a break from the GM'ing, but we definitely don't want to lose the hard work our computer did calculating all those universes. So we use the command
```
save
```
which will pickle the gamestate. After that we can make changes or even close the program, and come back to our previous state with
```
load
```
It's also possible to give a filename argument to these commands, like
```
save my-little-werewolf
```
to prevent files from overwriting each other. There's no warning about data being lost if you overwrite a previous file!

### Player actions
#### Wolf attacks
Okay, so now it's your player's turn! They will do the usual werewolf things with accusations and lying (okay, maybe not during the night), but they'll also have actions, and these actions will generate the evidence used to determine which universes are valid. The first thing your players will probably do is to use their werewolf powers and attack someone. We can register this with
```
attack Alice Bob
```
which means Alice attacked Bob. Make sure to only use this command when it's night-time, because the program will crash during the day.

#### Seer visions
Next part are the seer roles.
```
see Remus Bob
```
means that Remus used his seer action during the night (again, it'll crash during the day) because he wants to know if Bob is a good boy or not. The program will print an alignment, which is what you report back to your player. Once you have things to report back to your players, make sure to SAVE frequently and take backups each game phase!

Let's add a few more of these:
```
attack David Remus
attack Bob Alice
see David Alice
see Bob David
```
We do this because this will have an impact on the game state already. Try it with
```
namedtable
```
and spot the differences!

### Advancing the time
When all the sneaky night action has ended, it's time to switch to the next game phase: day 1. This is done with
```
next
```
It's very easy to forget to do this! Double-check and triple-check! Your actions (especially the wolf attacks) have to be registered on the right time, or the program will give wrong results.

(sidenote: in general forum werewolf, it's usually better to have no N0 wolf kills, and restricted N0 seer visions (like a random 'not evil' vision). This prevents games dying out early because of lucky kills/visions before the game even started. Not sure that is needed with quantum werewolf.)

### Death
During daytime, not much happens for the game master. You wait until your players have decided on a lynch. Then you do
```
kill Alice
```
which will kill off Alice on the current game time (again, make sure the time is right!). After this, do a
```
state
```
to see the role of the killed player, if you want to report this back to the players. It is possible that killing one player sets of a chain of events, killing other players or fixing their role!

And you basically keep using attack, kill, see, and next to run through the game (don't forget to save regularly), until you have a victory for either team. Victory conditions have to be checked manually.

### And of course..
The final command is
```
exit
```
which will throw away all your unsaved work (!) and exit the program.
