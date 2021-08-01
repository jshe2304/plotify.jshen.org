zip -r /mnt/d/documents/code/mysite.zip requirements.txt *.py app/*.py app/static/ app/templates/ .ebextensions/



@app.route('/spotify-playlist-utilities/<username>/combine', methods=['POST', 'GET'])
def spotifycombine(username):
    if not authenticated_user(username):
        return redirect('/spotify-playlist-utilities')

    playlists = all_playlists()
    albums = all_albums()

    playlist_choices = []
    for playlist in playlists:
        playlist_choices += (playlist['id'], playlist['name'])

    album_choices = []
    for album in albums:
        album_choices += (album['id'], album['name'])
    
    print ('here1')

    #class SpotifyCombineInstance(SpotifyCombineForm):
    #    pass

    print ('here2')

    setattr(SpotifyCombineForm, playlists, SelectMultipleField('Playlists', choices=playlist_choices))
    setattr(SpotifyCombineForm, albums, SelectMultipleField('Albums', choices=album_choices))

    print ('here3')

    form = SpotifyCombineForm()

    return render_template('spotify_combine.html', form=form)