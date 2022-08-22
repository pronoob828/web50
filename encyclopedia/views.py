import re
from sys import hash_info
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django import forms
import random


from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


# This function is my arch nemesis, I correct one thing and it ruins another.
# I did it? I did it!!!
def convert(content):

    # Standardizing line endings, got this idea when I looked at the source code of markdown2's convert function.
    # One of the few things that didn't go over my head.
    content = content.replace("\r\n", "\n")
    content = content.replace("\r", "\n")
    content = content + "\n\n"

    # Adding heading tags to all headings depending on number of hash symbols
    heading_pattern = re.compile(r"(?<!\\)(\n|^)(#{1,6})(\s+.*?)(?=\n)")
    headings = re.finditer(heading_pattern, content)
    for heading in headings:
        hx = len(heading.groups()[1])
        content = re.sub(
            heading.group(),
            "\n<h" + str(hx) + ">" + heading.groups()[2] + "</h" + str(hx) + ">\n",
            content,
            count=1,
        )

    # Detecting unordered list
    ul_pattern = re.compile(r"(?ms)\n\n(?<!\\)\*\s(.+?)\n\n")
    u_lists = re.finditer(ul_pattern, content)
    ul_spans = []
    for ul in u_lists:
        ul_spans.append(ul.start())
        ul_spans.append((ul.end() + 11))
        content = re.sub(
            re.escape(ul.group()), "<ul>" + ul.group() + r"</ul>\n\n", content,count=1
        )
        

    # Adding list items to list
    li_pattern = re.compile(r"(?m)(?<!\\)(^\*)(?=\s+)(.+?)(?=\n)")
    list_items = re.finditer(li_pattern, content)
    for item in list_items:
        for i in range(0,len(ul_spans),2):
            if  ul_spans[i] < item.start() < ul_spans[i+1]:
                content = re.sub(
                    re.escape(item.group()), "<li>" + item.groups()[1] + "</li>", content,count=1
                )

    # Detecting and substituting links
    link_pattern = re.compile(r"(?<!\\)\[(.+?)(?<!\\)\]((?<!\\)\(.+?(?<!\\)\))")
    links = re.finditer(link_pattern, content)
    for link in links:
        content = re.sub(
            re.escape(link.group()),
            "<a href=" + link.groups()[1] + ">" + link.groups()[0] + "</a>",
            content,
            count=1,
        )

    # Adding <b> tag to bold text
    bold_pattern = re.compile(r"(?<!\\)(\*|_){2}(?!\s)(.+?)(?<!\\)(\*|_){2}")
    bold_texts = re.finditer(bold_pattern, content)
    for bold_text in bold_texts:
        content = re.sub(
            re.escape(bold_text.group()),
            "<b>" + bold_text.groups()[1] + "</b>",
            content,
            count=1,
        )

    # Adding <i> tag to italic text
    italic_pattern = re.compile(
        r"(?<!\<br\>)(?<!\\)(\*|_){1}(?!\s)(.+?)(?<!\\)(\*|_){1}"
    )
    italic_texts = re.finditer(italic_pattern, content)
    for italic_text in italic_texts:
        content = re.sub(
            re.escape(italic_text.group()),
            "<i>" + italic_text.groups()[1] + "</i>",
            content,
            count=1,
        )
    
    # Paragraph detection... This was hell.
    para_pattern = re.compile(r"(\n\s*\n|^)((?!\n*\</?h|\n*\</?ul|\n*\</?li).+?)(?=\n\s*\n|\n*\<h|\n*\<ul|\n*\<li|$)",re.DOTALL)
    paras = re.finditer(para_pattern, content)
    for para in paras:
        content = re.sub(
            re.escape(para.group()), "<p>" + para.groups()[1] + "</p>", content, count=1
        )

    # Adding line breaks when detecting markdown linebreak (double space or back slash)
    newline_pattern = re.compile(r"(?<!\n)[\s]*(  |\\)\n[\s]*(?!\n)")
    content = re.sub(newline_pattern,"<br>",content)

    # Removing excess newlines (just to clean things up)
    content = content.replace("\n","")

    # Removing \ when before special characters
    content = content.replace("\*","*")
    content = content.replace("\#","#")
    content = content.replace("\_","_")
    return content


def display(request, entry):
    content = util.get_entry(entry)

    if not content:
        return render(request, "encyclopedia/not_found.html")

    content = convert(content)

    return render(
        request, "encyclopedia/display.html", {"content": content, "entry": entry}
    )


def search(request):
    query = request.GET["q"]
    query = str(query)
    entries = util.list_entries()
    sub_of = []
    for entry in entries:
        if entry.lower() == query.lower():
            return HttpResponseRedirect("/" + query)
        if query.lower() in entry.lower():
            sub_of.append(entry)

    return render(request, "encyclopedia/search.html", {"entries": sub_of})


class CreateForm(forms.Form):
    title = forms.CharField(label="Page Title")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 25, "cols": 25}))


def create(request):

    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            entries = util.list_entries()
            for entry in entries:
                if title.lower() == entry.lower():
                    return HttpResponse("<h1>Error: Title already in use</h1>")

            try:
                util.save_entry(title, content)
                return HttpResponseRedirect("/" + title)
            except:
                return HttpResponse("Something went wrong")

        return HttpResponseRedirect("")
    else:
        return render(request, "encyclopedia/create.html")


class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 25, "cols": 25}))
    entry = forms.CharField()


def edit(request):

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data["content"]
            current_entry = form.cleaned_data["entry"]
            try:
                new_content = new_content.replace("\r","")
                util.save_entry(current_entry, new_content)
            except:
                return HttpResponse("<h1>Something's wrong!</h1>")
        return HttpResponseRedirect("/" + current_entry)
    else:
        entry = request.GET["entry"]
        content = util.get_entry(entry)
        content = content.replace("\r\r","")
        return render(
            request, "encyclopedia/edit.html", {"entry": entry, "content": content}
        )


def rand(request):
    R = random.choice(util.list_entries())
    return HttpResponseRedirect("/" + R)
