# LoL Global Power Ranking
LoL Global Power Ranking Repo for eponym [hackathon](https://lolglobalpowerrankings.devpost.com/)

## Table of content
- [LoL Global Power Ranking](#lol-global-power-ranking)
  - [Table of content](#table-of-content)
  - [Informations](#informations)
  - [Objectives](#objectives)
  - [Requirements](#requirements)
  - [Criteria](#criteria)
  - [Pondering](#pondering)
  - [What already exists](#what-already-exists)
  - [What to take into account](#what-to-take-into-account)
  - [Possible solution](#possible-solution)
    - [Functionnal](#functionnal)
    - [Technical](#technical)
      - [Database](#database)
      - [Server](#server)
      - [Web application](#web-application)
  - [Mathematical considerations](#mathematical-considerations)
    - [Elo rating](#elo-rating)
    - [Game competitiveness](#game-competitiveness)
    - [Player score](#player-score)
    - [Start of season team elo](#start-of-season-team-elo)
  - [References](#references)
  - [Authors](#authors)

## Informations
All external website, application, or other non solution related objects will be mentionned in the [references](#references) part of this study.

This document should constantly evolved to take into account any new informations that arise during the life of the solution.

## Objectives
Creating any kind of application capable of giving an accurate ranking for a given list of team / competitions in the LoLEsports ecosystem.
This must work globally and on a set group teams.
In case of tournaments, it must give the final ranking of the tournaments.

## Requirements
The given solution must use the data provided by lolesports for the hackathon, and at least one AWS service.

## Criteria
Taken from the hackathon summary, the 4 criteria are :
- Technological implementations: The quality of the project technological side.
- Design: User experience.
- Quality of the idea: How innovative is the solution.
- Interpretability: How well can we explain our solution.

Outside of these factors, the solution MUST give a somewhat accurate power ranking to be considered.  
These factors seems to be in order of importance, as in case of a tie the first ones will be looked at first.

## Pondering
Many questions arise from this premise, here is a list of relevant ones :
- How do we treat best of series ?
- How do we evaluate the value a player bring to a team ?
- How do we take into account game competitiveness ?
- How do we rank team accross regions and leagues ?
- How do we take into account upsets happening in tournaments predictions ?
- How do we treat the data from experimental games ?
- Should all games be the same weight ?

## What already exists
We can take notes that a few method already exists for ranking team in other sports, such as the FIFA World Ranking, the Opta's Power Ranking or the HoopsHype's Global Rating system. These are but a few exemples, and more information can be found about them in the [references](#references) section.  

It must be noted that there are already a few web sites and applications that provides global LoL teams ranking. A few examples include GosuGamers, Tips.gg, Ensiplay.com, and getesports.net.  

There is also a number of articles about creating your own Elo Rating system, such as the one by Matt Mazzola on Medium.

## What to take into account
Specific things to take into account includes :
- Players : The players are the main part of the team, and there is an obvious need to figure out a value for each player.
- League : Where a team is evolving might tell a lot about it's current rank. Even in one region, there are multiples leagues and they are not all on the same level.
- Value of a match : Not all match are as relevant, while all are valuable, some might be used by better team in order to improve on weaknesses, and as such, increase the possibility of an upset.
- Game result : The result of a game is obviously more indicative about the two team current level of play than any other factor.
- Region rating : Each region has a different rating, as not each region is as strong as the other. Sea Chinese and Korean domination since 2013.
- Game competitiveness : How close was the game, did the team winning nearly lost, was it a stomp...

## Possible solution

### Functionnal
The user must be welcome by an intuitive and fast interface. It should offer all ways of customisation (selecting teams, regions, tournaments, leagues...) and display data according to what was selected. If a player score is calculated, it should also offer ways to display this player score.

The data calculation should not happen when user wants to retrieve it, as to avoid long and unnecessary waiting period.

### Technical
One of easiest and most practical solution would be to create a web application and a server, with a database.  

#### Database
The database will simply hold all the data from teams, region, leagues and players.

#### Server
The server will be responsible for treating any new data, storing it in the database, and answering requests from the web application.

#### Web application
The web application will profite the interface for the user to retrieve (and possibly add) data from the server / database. It will only communicate directly with the server, and must be quick so that user do not wait or experience lag.

## Mathematical considerations

### Elo rating
Elo Rating system calculus for probability of team A win :  

$E_{a} = \frac{1}{1 + 10 \frac{elo_{A} - elo_{B}}{400}}$

Elo Rating system calculus for elo change :  

$elo_{A}' = elo_{A} + K(S_{A} - E_{A})$

Where $elo_{A}$ and $elo_{B}$ are the elo of Team  respectively A and B, $K$ is the variable used to calculate new elo, $S_{A}$ is the final scoreline and $E_{A}$ is the expected outcome of the game.

### Game competitiveness

### Player score
Player score ($p_{n}$) represents the value of player $n$ at the start of the split.
Base player score is 1000, then calculated with all data from games played before split, weighted to give more value to most recent games.

### Start of season team elo

$elo_{p} = \frac{(p_{1} + p_{2} + p_{3} + p_{4} + p_{5})}{5}$  
$elo_{team} = elo_{p} + \frac{elo_{old} - elo_{p}}{R}$

Where $elo_{p}$ is the base elo of players put together, $p_{n}$ is the player score of player $n$, $elo_{team}$ is the final team elo, $elo_{old}$ is the previous team elo and $R$ is the regularity ratio of the team, ie. how regular is the team.

R is calculated with the following method, only if $n > 1$ :

$R = \frac{\sum(elo_{n}-elo_{average})}{n - 1}$

## References
- [Hackathon](https://lolglobalpowerrankings.devpost.com/)
- [FIFA World Ranking](https://digitalhub.fifa.com/m/f99da4f73212220/original/edbm045h0udbwkqew35a-pdf.pdf)
- [Opta's Power Rankings](https://theanalyst.com/eu/2023/01/power-rankings-your-club-ranked/)
- [HoopsHype's Global Rating](https://hoopshype.com/2021/10/26/what-is-hoopshypes-global-rating/)
- [Medium article on implementing Elo Rating system](https://mattmazzola.medium.com/implementing-the-elo-rating-system-a085f178e065)
- [GosuGamers](https://www.gosugamers.net/lol/rankings)
- [Tips.gg](https://tips.gg/lol/teams/)
- [Ensiplay.com](https://ensiplay.com/teams/lol)
- [Getesports.net](https://getesports.net/en/lol-teams/)

## Authors
MiniWolskys