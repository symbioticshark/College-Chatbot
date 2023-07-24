
import webbrowser
import tkinter as tk
from functools import partial
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('data.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    x=res.split()
    #resp=''
    #for i in x:
     #   if i.startswith("https:") or i.startswith("http:"):
    #       resp=i
     #       return urllib.parse.quote_plus(resp)
    return res


def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)


def findUrl(string):
    x=string.split()
    res=''
    url=False
    for i in x:
        if i.startswith("https:") or i.startswith("http:"):
            url=True
    return url

def callback(url):
   webbrowser.open_new_tab(url)

def insert_hyperlink(self, tag_name, hyperlink_text, hyperlink_url):
        """
        The function inserts a text in a tkinter text box and converts it to a hyperlink using spesial tags and event functions.
        :param tag_name: an unic tag name for each hyperlink is nessesary
        :param hyperlink_text: Text
        :param hyperlink_url: a Weblink or a file link
        """
        
        # Get current cursor position
        cursor_pos = self.index(tk.INSERT)

        # Insert hyperlink text
        self.insert(tk.INSERT, hyperlink_text)

        # Add hyperlink tag to text
        start_idx = cursor_pos
        end_idx = f"{cursor_pos}+{len(hyperlink_text)}c"
        self.tag_add(tag_name, start_idx, end_idx)

        # Configure hyperlink tag to be clickable
        self.tag_configure(tag_name, foreground="blue", underline=True)

        # cursor changes to a hand when over a hyperlink
        def on_hyperlink(event):
            self.configure(cursor="hand2")

        # cursor changes back when off a hyperlink
        def off_hyperlink(event):
            self.configure(cursor="")

        # Define hyperlink click event
        def on_hyperlink_click(event):
            webbrowser.open(hyperlink_url)

        # Bind an event function to change cursor to hand when over hyper link text
        self.tag_bind(tag_name, "<Enter>", on_hyperlink)
        self.tag_bind(tag_name, "<Leave>", off_hyperlink)

        # Bind a hyperlink tag to a click event
        self.tag_bind(tag_name, "<Button-1>", on_hyperlink_click)


#Creating GUI with tkinter
from tkinter import *


def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        res = chatbot_response(msg)
        url = findUrl(res)
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
    
        if(url == True):
            ChatLog.insert(END, "Bot:Please click on this link ")
            insert_hyperlink(ChatLog,'google',res,res) 
            ChatLog.insert(END, "\n\n")
        
        else:ChatLog.insert(END, "Bot: " + res + '\n\n')
            
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
 

base = Tk()
base.title("College Chatbot")
base.geometry("600x460")
base.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font=("Verdana",9,'bold'))

ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview)
ChatLog['yscrollcommand'] = scrollbar.set

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial",foreground='black')
#EntryBox.bind("<Return>", send)

#Create Button to send message
SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
                    command= send )




#Place all components on the screen
scrollbar.place(x=583,y=6, height=486)
ChatLog.place(x=6,y=6, height=386, width=600)
EntryBox.place(x=6, y=401, height=50, width=465)
SendButton.place(x=471, y=401, height=50)

base.mainloop()