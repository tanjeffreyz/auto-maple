<h1 align="center">
  Auto Maple
</h1>

Auto Maple is a Python program that plays MapleStory, a 2D side-scrolling MMORPG, using simulated key presses, TensorFlow machine learning, OpenCV template matching, and other computer vision techniques.

<br />






<h2 align="center">
  Minimap
</h2>

<img align="right" src="https://user-images.githubusercontent.com/69165598/123177212-b16f0700-d439-11eb-8a21-8b414273f1e1.gif" width="400"/>

Auto Maple uses OpenCV template matching to determine the bounds of the minimap as well as the various elements within it, allowing it to accurately track
the player's in-game position. If "record_layout" is set to "True" in the routine file, Auto Maple will record the player's previous positions in a quadtree-based Layout object, which is periodically saved to a file in the "layouts" directory. Every time a new routine is loaded, its corresponding layout file, if it exists, will also be loaded. This Layout object uses the A* search algorithm on its stored points to calculate the shortest path from the player to any target location, which can dramatically improve the accuracy and speed at which routines are executed.

<br clear="right"/>






<h2 align="center">
  Command Books
</h2>

Designed with modularity in mind, Auto Maple can operate any character in the game as long as it is provided with an appropriate list of in-game actions, or a "command book". A command book is a Python file that contains multiple classes, one for each in-game ability, that tells the program what keys it should press and when to press them. Once a command book is imported, its classes are automatically compiled into a dictionary that Auto Maple can then use to interpret commands within routines. Commands have access to all of Auto Maple's global variables, which allow them to change their behavior based on the state of the game.

<br clear="left"/>






<h2 align="center">
  Runes
</h2>


<br clear="right"/>






<h2 align="center">
  Routines
</h2>

<p>
  <a href="https://user-images.githubusercontent.com/69165598/123182117-9d300780-d443-11eb-890b-c11edbe5f1d0.jpg">
    <img align="left" src="https://user-images.githubusercontent.com/69165598/123300035-fa24cf80-d4ce-11eb-8d43-eae94fa2a914.jpg"/>
  </a>
</p>

A routine is a user-created CSV file that tells Auto Maple where to move and what abilities and commands to use at each location. A custom-made interpreter within Auto Maple parses through the selected routine and converts the routine into a list of objects that can then be executed by the program. An error message is printed for every line that contains invalid parameters, and those lines are ignored during the conversion.

The "\*" symbol creates a new Point object, which represents an in-game location. Each Point object will store the commands listed below it, and will execute them in that order once the player reaches that Point. The "@" symbol indicates that the following parameter is a label, which can be jumped to using the "goto" command. Lastly, "s" is used to set the value of certain global variables in config.py, which allows the user to create different settings specific to each routine.

(Click the image to see more of the routine).

<br clear="left"/>







<h2 align="center">
  Video Demonstration
</h2>

<p align="center">
  Click the below image to see Auto Maple in action:
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg">
    <img src="https://img.youtube.com/vi/qs8Nw55edhg/0.jpg"/>
  </a>
</p>
