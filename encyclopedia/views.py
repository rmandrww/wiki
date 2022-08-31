from django.shortcuts import render, redirect
from django import forms
import random

from . import util
import markdown2

# This class defines the form required to edit an article and its respective styles

class ArticleForm(forms.Form):
    title = forms.CharField(label="Title" )
    content = forms.CharField(max_length = 20000, label = "Content", widget=forms.Textarea(attrs = {'cols': 'auto',
    'rows': '5',
    'placeholder': '# Title \n\nStart typing your article here!'}))

    title.widget.attrs.update({'class': 'titlebox', 'placeholder': 'Name your entry'})
    content.widget.attrs.update({'class': 'contentbox'})

# Returns a page with a list of all the entries and its lenght

def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "total_entries": len(entries),
    })

# Returns a page with the contents of an entry or an error page if it doesn't exist

def entry (request, entry):
    try:
        content = markdown2.markdown(util.get_entry(entry), extras=["tables", "fenced-code-blocks"])
        return render(request, "encyclopedia/entry.html", {"content": content, "entry": entry})
    except TypeError:
        return render (request, "encyclopedia/404.html", {"entry": entry.capitalize()})

# Returns a page with a list of all the entries that contains the get request as a substring
# If there is an exact match, redirects to that entry instead
# If there aren't any results then displays an error message

def search (request):
    # List with all the entries
    entries = util.list_entries()
    results = []
    input = request.GET['q']
 
    for entry in entries:
        # If there is an exact match between the input and the entry it redirects to it
        if input.lower() == entry.lower(): return redirect("wiki:entry", input)
        # If the input exists as a substring inside the entry the last gets appended to the results list
        elif input.lower() in entry.lower(): results.append(entry)
        # Otherwise check the next element
        else: continue

    if results == []: empty = 1
    else: empty = 0

    return render(request, "encyclopedia/search.html", {
        "entries": results,
        "empty": empty,
        "input": input,
    })

# Redirects to a random page in the entry list

def randompage (request):
    a = random.choice(util.list_entries())
    return redirect ("wiki:entry", a)

# If it receives a get request, displays the form for the creation of a new entry

# Then when receiving a post request, it creates a new markdown file with the contents filled by the user

def newpage (request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            entries = util.list_entries()
            for entry in entries:
                if form.cleaned_data["title"] == entry:
                    return render (request, "encyclopedia/new.html", {
                    "form": form,
                    "error": 'This article already exist!'})
            
            util.save_entry(form.cleaned_data["title"], form.cleaned_data["content"])
            return redirect("wiki:entry", form.cleaned_data["title"])
    return render (request, "encyclopedia/new.html", {
        "form": ArticleForm(),
        "error": '',
    })

# When receving a get request, displays a form similar to the one in the newpage view
# but it comes already filled with the contents of its corresponding markdown file

# Then when it receives a post request by the user it overwrites the entry with the data in the new request

# The user can't change the name of the file by design

def editpage (request, entry):
    if request.method == "POST":
        form = ArticleForm (request.POST)
        if form.is_valid():
            print(form.cleaned_data["content"])
            util.save_entry(form.cleaned_data["title"],form.cleaned_data["content"])
            return redirect("wiki:entry", form.cleaned_data["title"])
        else:
            return render (request, "encyclopedia/new.html", {
            "form": form,
            "error": 'Invalid Form',
            "entry": entry
        })

    else:
        form = ArticleForm ({'title': entry, 'content': util.get_entry(entry)})
        return render (request, "encyclopedia/edit.html", {
        "form": form,
        "error": '',
        "entry": entry
        })