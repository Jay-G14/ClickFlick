## Steps to Run in Virtual Environment:

Navigate to the directory where isslab3.py exists in the terminal.

In the terminal, execute the following commands:

```bash
python3 -m venv venv
./run.sh
```

Details about the website being opened will be displayed in the terminal.

To access the site for login, type in the link provided in the terminal. For example, it might show http://127.0.0.1:5000/login

To access the home page, navigate to http://127.0.0.1:5000/main 

## Additional Information:

If Flask is not working, you can refer to this link for installation on Ubuntu 20.04: How to Install Flask on Ubuntu 20.04.

Also, once flask is set up, just run run.sh in the directory.

## Assumptions:

- Login page is in home page
- Images can be uploaded by drag and drop as well as selected and multiple images are suppoerted
- There is checkbox on the top corner of the photos which allows user to order the photos for the video
- Clicking on it allots it in
- There is a drop down menu on the other top corner (threee dots) with which you can specify duration and transition for each image
- The photo selection works like ms lens ordering, clicking selects it and allots the highest number+1
- Deselecting it decrements the images higher than it by one
- You can add multiple bg music to the video
- Play pause can be toggled with spacebar
- Rewind and fastforward with arrow keys
- Right clicking on video gives you multiple options such as playback speed etc
- Functions such as download will be added later
- using username: admin password:admin leads to admin screen
- We are assuming the flask server is up and running and the exchange token is done
- Download and resolution button will be made functional later
- For now, only admin pages work. Login and register will be implemented later on. Security protocols must be observed.

