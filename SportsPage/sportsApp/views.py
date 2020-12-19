from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from bs4 import BeautifulSoup
import requests
from csv import writer

# View Login Page
def loginPage(request):
    return render(request, 'login.html')

# login existing user created by Admin #
def login(request):
    errors = User.objects.return_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    login_user_list = User.objects.filter(email=request.POST['email'])
    logged_in_user = login_user_list[0]
    request.session['user_id'] = logged_in_user.id
    return redirect('/dashboard')

# logs in a new user if validations pass #
def new_user(request):
    errors = User.objects.new_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        name= request.POST['name']
        email= request.POST['email']
        password= request.POST['password']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(name=name, home=home, email=email, password=pw_hash)
        request.session['user_id'] = new_user.id
    return redirect('/dashboard')

# main dashboard page #
def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('/')
    user = User.objects.get(id=request.session['user_id'])
    groupResponse = requests.get('https://www.covers.com/sports/nfl/matchups')
    soup = BeautifulSoup(groupResponse.text, 'html.parser')
    post = soup.find_all(class_='cmg_game_data cmg_matchup_game_box')
    groupArr = []
    for post in post:
        # create new dictonary to store each match details
        matchDict = {}
        # Date of match
        matchDict["date"] = post.find(class_='cmg_matchup_header_date').get_text()
        matchDict["time"] = post.find(class_='cmg_game_time').get_text().replace('ET', '')
        # Match odds
        matchDict['openingOdds'] = post.find(class_='cmg_team_opening_odds').get_text()
        matchDict['liveOdds'] = post.find(class_='cmg_team_live_odds').get_text()
        # Home Team Details
        Hteam = post.find(class_='cmg_matchup_list_column_3').find(class_='cmg_team_name')
        Hteam.span.decompose()
        HomImg = post.find(class_='cmg_matchup_list_column_3').find(class_='cmg_team_logo').findChildren("img")
        matchDict["homeTeam"] = Hteam.get_text()
        matchDict["homeTeamPic"] = HomImg[0]["src"]
        matchDict["homeBet"] = post.find(class_='cmg_matchup_list_column_3').find(class_='cmg_matchup_list_odds_value').get_text()
        matchDict["homeL10"] = post.find(class_='cmg_l_col cmg_l_span_6 cmg_matchup_in_short_condensed_home').find(class_='cmg_matchup_in_short_condensed_home_lastten').get_text().replace('(', ' (').replace(':', ': ')
        # Opponent Team Details
        Oteam = post.find(class_='cmg_team_name')
        Oteam.span.decompose()
        OppImg = post.find(class_='cmg_team_logo').findChildren("img")
        matchDict["oppTeam"] = Oteam.get_text()
        matchDict["oppTeamPic"] = OppImg[0]["src"]
        matchDict["oppBet"] = post.find(class_='cmg_matchup_list_odds_value').get_text()
        matchDict["oppL10"] = post.find(class_='cmg_l_col cmg_l_span_6 cmg_matchup_in_short_condensed_away').find(class_='cmg_matchup_in_short_condensed_away_lastten').get_text().replace('(', ' (').replace(':', ': ')
        # append created dictionary to group array
        groupArr.append(matchDict);
        # get url for scraping details for each team
        url = post.find(class_='cmg_team_logo').findChildren("a")[0]["href"]
        TeamResponse = requests.get(f"https://www.covers.com{url}")

    context = {
        'user': user,
        'groupArr':groupArr,
    }
    return render(request, 'dashboard.html', context)

# logout function
def logout(request):
    request.session.flush()
    return redirect('/')