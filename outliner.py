"""
 "  File: outliner.py
 "  Written By: Gregory Owen
 "
 "  Description: An easy way to synthesize notes into an essay outline.
""" 

from Tkinter import *
from tkFileDialog import *
from collections import deque
from operator import itemgetter
import tkSimpleDialog
import tkMessageBox
import json

from outlinergui import OutlinerGUI

"""
Fields in a topic:
  name:    Subject of the topic, used to index into Outliner.topics (string)
  notes:   Notes in the topic (list of strings)
  number:  Number of topics created before this one (int)
  line:    Information line about the topic on the main screen (Tkinter.Frame)
  frame:   Frame containing this topic's dndlist (Tkinter.Frame)
  dndlist: DNDList containing this topic's notes (DNDList.dndlist)
"""

class Outliner():

    def __init__(self, master=None):
        self.root = master
        self.filename = None
        self.topics = {}
        self.notes = deque()

        self.gui = OutlinerGUI(self)

    def newProject(self):
        """ Create a new project. """
        
        notepath = askopenfilename()

        if notepath is not None:
            notefile = open(notepath, 'r')
            self.notes = deque()
            
            for note in notefile.read().strip().split("\n"):
                if note != "":
                    self.notes.append(note)

            self.gui.displayNextNote()

    def openProject(self):
        """ Open a previous project from its .otln file. """
        
        projectPath = askopenfilename(filetypes=[("Outliner files", "*.otln")])

        if projectPath is None:
            return
        if projectPath[-5:] != ".otln":
            errorPrompt = "I'm sorry, but that file is not a valid input type.\n\
Please choose a valid Outliner file (.otln)"
            tkMessageBox.showerror("Error: Invalid File Type", errorPrompt)
            return

        self.filename = projectPath
        projectFile = open(projectPath, 'r')

        noteList = projectFile.readline()
        self.notes = deque(json.loads(noteList))

        topicDict = projectFile.readline()
        self.topics = json.loads(topicDict)

        projectFile.close()

        self.gui.displayNextNote()

        # Sort the topics by number
        sortedTopicNames = sorted(self.topics,
                                  key=(lambda name: self.topics[name]['number']))
        
        for name in sortedTopicNames:
            topic = self.topics[name]
            topic['line'] = self.gui.newTopicLine(topic)
            topic['frame'], topic['dndlist'] = self.gui.newTopicFrame(topic)
            self.gui.menu.addToTopicLists(topic)

    def saveProject(self):
        """ Save the current state of the project. """
        
        if self.filename is None:
            self.saveProjectAs()
        else:
            self.sortTopics()
            self.sortNotes()

            outfile = open(self.filename, 'w')
            outfile.write(json.dumps(list(self.notes)))
            outfile.write("\n")
            outfile.write(json.dumps(self.topics, default=self.handleJSON))
            outfile.close()

    def saveProjectAs(self):
        """ Save the project under a new name. """
        
        options = {}
        options['defaultextension'] = '.otln'
        options['filetypes'] = [('all files', '.*'), ('Outliner files', '.otln')]
        options['title'] = 'Save your outline'

        self.filename = asksaveasfilename(**options)

        if self.filename is not None:
            self.saveProject()

    def handleJSON(self, obj):
        """ Handles the JSON encoding of obj when obj would cause a TypeError. """

        return None

    def exportOutline(self):
        """ Create a .txt outline based off of the notes in the Outliner. """
        
        options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('Text files', '.txt')]
        options['title'] = 'Export your outline to a text file'
        
        exportFileName = asksaveasfilename(**options)

        if exportFileName is not None:
            self.sortNotes()
            self.sortTopics()

            outfile = open(exportFileName, 'w')
            # Write topics in the order given by their numbers
            for topic in sorted(self.topics.values(), key=itemgetter('number')):
                outfile.write(topic['name'] + ":\n")
                for note in topic['notes']:
                    outfile.write("\t" + note + "\n\n")
                outfile.write("\n")
            outfile.close()

    def quit(self):
        """ Quit the outliner. """

        self.root.quit()

    def newTopic(self):
        """ Create a new topic. """

        topicPrompt = "What would you like to call your new topic?"
        topicName = tkSimpleDialog.askstring("New Topic", topicPrompt)

        if topicName in self.topics:
            self.gui.topicAlreadyExists()
            topicName = None
            self.newTopic(button)

        if topicName is None:
            print "Error: no topic name"
            return

        newTopic = {}
        newTopic['name'] = topicName
        newTopic['notes'] = []
        newTopic['number'] = len(self.topics.keys())
        newTopic['line'] = self.gui.newTopicLine(newTopic)
        newTopic['frame'], newTopic['dndlist'] = self.gui.newTopicFrame(newTopic)

        self.gui.menu.addToTopicLists(newTopic)
        self.topics[topicName] = newTopic

    def addNoteToTopic(self, topic):
        """ Add the currently-displayed note to the topic. """

        if len(self.notes) > 0:
            note = self.notes.popleft()
            topic['notes'].append(note)
            self.gui.addNoteToGUI(topic, note)
            self.gui.displayNextNote()

    def viewTopic(self, topic):
        """ Display the notes that are part of the topic. """

        self.gui.viewTopic(topic)

    def nextNote(self):
        """ Display the next note in the list. """

        if len(self.notes) > 0:
            self.notes.append(self.notes.popleft())
            self.gui.displayNextNote()

    def prevNote(self):
        """ Display the last note in the list. """

        if len(self.notes) > 0:
            self.notes.appendleft(self.notes.pop())
            self.gui.displayNextNote()

    def sortNotes(self):
        """ Sort the notes in each topic according to the order in which they 
            are currently arranged. """
        
        for topic in self.topics.values():
            topic['notes'] = [node.widget.cget('text')
                              for node in topic['dndlist'].getOrdered()]
    def sortTopics(self):
        """ Assign numbers to topics according to the order in which they are
            currently arranged. """

        ordered = self.gui.topicList.getOrdered()
        for i in range(len(ordered)):
            topic = ordered[i].widget.topic
            topic['number'] = i

""" --------------------------------- main method ------------------------------- """

if __name__ == "__main__":
    root = Tk()
    outliner = Outliner(root)
    root.mainloop()
