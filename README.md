<h1 align="center">
  Auto Maple
</h1>

Auto Maple is a Python program that plays MapleStory, a 2D side-scrolling MMORPG, using simulated key presses, TensorFlow machine learning, OpenCV template matching, and other computer vision techniques.

<br>








<h2 align="center">
  Minimap
</h2>

<table align="center" border="0">
  <tr>
    <td>
Auto Maple uses OpenCV template matching to determine the bounds of the minimap as well as the various elements within it, allowing it to accurately track the player's in-game position. If "record_layout" is set to "True" in the routine file, Auto Maple will record the player's previous positions in a quadtree-based Layout object, which is periodically saved to a file in the "layouts" directory. Every time a new routine is loaded, its corresponding layout file, if it exists, will also be loaded. This Layout object uses the A* search algorithm on its stored points to calculate the shortest path from the player to any target location, which can dramatically improve the accuracy and speed at which routines are executed.
    </td>
    <td width="400px">
      <img align="center" src="https://user-images.githubusercontent.com/69165598/123177212-b16f0700-d439-11eb-8a21-8b414273f1e1.gif"/>
    </td>
  </tr>
</table>

<br>








<h2 align="center">
  Command Books
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123372905-502e5d00-d539-11eb-81c2-46b8bbf929cc.gif" width="900px"/>
</p>
  
<table align="center" border="0">
  <tr>
    <td width="900px">
Designed with modularity in mind, Auto Maple can operate any character in the game as long as it is provided with a list of in-game actions, or a "command book". A command book is a Python file that contains multiple classes, one for each in-game ability, that tells the program what keys it should press and when to press them. Once a command book is imported, its classes are automatically compiled into a dictionary that Auto Maple can then use to interpret commands within routines. Commands have access to all of Auto Maple's global variables, which can allow them to actively change their behavior based on the player's position and the state of the game.
<br><br>
The above video shows Auto Maple consistently performing a mechanically advanced ability combination.
    </td>
  </tr>
</table>
  
<br>







<h2 align="center">
  Routines
</h2>

<table align="center" border="0">
  <tr>
    <td width="400px">
      <p align="center">
        <a href="https://user-images.githubusercontent.com/69165598/123182117-9d300780-d443-11eb-890b-c11edbe5f1d0.jpg">
          <img src="https://user-images.githubusercontent.com/69165598/123300035-fa24cf80-d4ce-11eb-8d43-eae94fa2a914.jpg" width="400px"/>
        </a>
      </p>
    </td>
    <td>
A routine is a user-created CSV file that tells Auto Maple where to move and what abilities and commands to use at each location. A custom-made interpreter within Auto Maple parses through the selected routine and converts it into a list of objects that can then be executed by the program. An error message is printed for every line that contains invalid parameters, and those lines are ignored during the conversion.
<br><br>
The "*" symbol creates a new Point object, which represents an in-game location. Each Point object will store the commands listed below it, and will execute them in that order once the player reaches that Point. The "@" symbol indicates that the following parameter is a label, which can be jumped to using the "goto" command. This can be used to create loops and organize routines into sections. Lastly, "s" is used to set the value of certain global variables during runtime, which allows the user to save different settings specific to each routine.
<br><br>
(Click the image on the left to see more of the routine).
    </td>
  </tr>
</table>

<br>








<h2 align="center">
  Runes
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="900px"/>
</p>

<table align="center" border="0">
  <tr>
    <td width="900px">
Auto Maple has the ability to automatically solve "runes", or in-game arrow key puzzles. It first uses OpenCV's color filtration and Canny edge detection algorithms to isolate the arrow keys and reduce as much background noise as possible. Then, it runs multiple inferences on the preprocessed frames using a custom-trained TensorFlow RNN model until two inferences agree. Because of this preprocessing, Auto Maple is extremely accurate at solving runes in all kinds of (often colorful) environments.
    </td>
  </tr>
</table>


<br>









<h2 align="center">
  Video Demonstration
</h2>

<p align="center">
  Click the below image to see Auto Maple in action:
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=qs8Nw55edhg">
    <img src="https://user-images.githubusercontent.com/69165598/123308656-c5b61100-d4d8-11eb-99ac-c465665474b5.gif" width="600px"/>
  </a>
</p>
