from django.shortcuts import render, redirect
from django import forms
import random

from . import util
import markdown2

class SearchForm(forms.Form):
    search = forms.CharField(label="Search")

def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "total_entries": len(entries),
    })

def entry (request, entry):
    try:
        content = markdown2.markdown(util.get_entry(entry), extras=["tables", "fenced-code-blocks"])
        return render(request, "encyclopedia/entry.html", {"content": content, "entry": entry})
    except TypeError:
        return render (request, "encyclopedia/404.html", {"entry": entry.capitalize()})

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

def randompage (request):
    a = random.choice(util.list_entries())
    return redirect ("wiki:entry", a)
