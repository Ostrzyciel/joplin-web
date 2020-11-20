# coding: utf-8
"""
   joplin-web
"""
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from joplin_api import JoplinApiSync
from joplin_web.forms import NoteForm, FolderForm, TagForm
from joplin_web.utils import tag_for_notes
import logging

from rich import console
console = console.Console()

logger = logging.getLogger("joplin_web.app")

joplin = JoplinApiSync(token=settings.JOPLIN_WEBCLIPPER_TOKEN)


def home(request, *args, **kwargs):
    template_name = "index.html"
    form_folder = FolderForm()
    form_tag = TagForm()
    res = joplin.get_notes()
    notes = tag_for_notes(res)

    form = NoteForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            parent_id = form.cleaned_data['parent_id']
            tags = form.cleaned_data['tags']
            data = dict()
            data['tags'] = tags
            res = joplin.create_note(title=title, body=text, parent_id=parent_id, **data)
            form = NoteForm()
    else:
        form = NoteForm()
    console.print(len(notes))
    context = {"notes": notes, "form": form, 'form_tag': form_tag, 'form_folder': form_folder}

    return render(request, template_name, context)


def edit_note_and_tags(request, note_id, *args, **kwargs):
    """
    edit one note and provide its tags too
    :param request
    :param note_id the note to modify
    :return HttpResponse
    """
    template_name = "index.html"
    # to keep only the data of the folder if provided
    folder_id = request.GET.get('folder_id', '')
    tag_id = request.GET.get('tag_id', '')
    if folder_id:
        notes = joplin.get_folders_notes(folder_id)
        # res = joplin.get_folders_notes(folder_id)
        # notes = tag_for_notes(res)
    elif tag_id:
        notes = joplin.get_tags_notes(tag_id)
    else:
        notes = joplin.get_notes()

    note = joplin.get_note(note_id)

    data = note.json()
    tags = joplin.get_notes_tags(data['id'])

    if request.POST:
        form = NoteForm(request.POST, initial={'parent_id': data['parent_id']})
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            parent_id = form.cleaned_data['parent_id']
            data = dict()
            data['tags'] = form.cleaned_data['tags']
            res = joplin.update_note(note_id=note_id, title=title, body=text, parent_id=parent_id, **data)
            if res.status_code == 200:
                messages.add_message(request, messages.INFO, "Note updated successfully")
    else:
        form = NoteForm()
        tags_list = []
        for tag in tags.json()['items']:
            tags_list.append(tag['id'])
        form.initial['tags'] = tags_list
        form.initial['parent_id'] = data['parent_id']
        form.initial['title'] = data['title']
        form.initial['text'] = data['body']

    context = {"notes": notes.json()['items'],
               "note": note,
               "note_id": note_id,
               "folder_id": folder_id,
               "tag_id": tag_id,
               "form": form}

    return render(request, template_name, context)


def notes_folder(request, folder_id, *args, **kwargs):
    """
    get all the notes of that folder
    :param request
    :param folder_id: id of the folder we want to filter
    :return HttpResponse
    """
    template_name = "index.html"
    res = joplin.get_folders_notes(folder_id)
    notes = res.json()['items'] if 'items' in res.json() else []
    form = NoteForm()
    context = {"notes": notes, "form": form, 'folder_id': folder_id}
    return render(request, template_name, context)


def notes_tag(request, tag_id, *args, **kwargs):
    """
    get all the notes of that tag
    :param request
    :param tag_id: id of the tag we want to filter
    :return HttpResponse
    """
    template_name = "index.html"
    res = joplin.get_tags_notes(tag_id)
    notes = res.json()['items'] if 'items' in res.json() else []
    form = NoteForm()
    context = {"notes": notes, "form": form, 'tag_id': tag_id}

    return render(request, template_name, context)


def create_folder(request):
    form = FolderForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            title = form.cleaned_data['title']
            joplin.create_folder(title)
    return HttpResponseRedirect(reverse('home'))


def create_tag(request):
    form = TagForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            title = form.cleaned_data['title']
            joplin.create_tag(title)
    return HttpResponseRedirect(reverse('home'))


def delete_note(request, note_id, *args, **kwargs):
    """
    delete a note
    :param request
    :param note_id: id of the folder we want to delete
    :return HttpResponse
    """
    joplin.delete_note(note_id)
    return HttpResponseRedirect(reverse('home'))


def delete_tag(request, tag_id, *args, **kwargs):
    """
    delete a tag
    :param request
    :param tag_id: id of the tag we want to delete
    :return HttpResponse
    """
    joplin.delete_tag(tag_id)
    return HttpResponseRedirect(reverse('home'))


def delete_folder(request, folder_id, *args, **kwargs):
    """
    delete a folder
    :param request
    :param folder_id: id of the folder we want to delete
    :return HttpResponse
    """
    joplin.delete_folder(folder_id)
    return HttpResponseRedirect(reverse('home'))
