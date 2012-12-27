# -*- coding: utf-8 -*-
from django import forms

class torrentForm(forms.Form):
    torfile = forms.FileField(
        label='Select a torrent file',
        required=False
    )
    torlink = forms.CharField(
        label='or link to the torrent:',
        required=False
    )
    '''
    magling = forms.CharField(
        label='or magnet link:',
        required=False
    )
    '''
