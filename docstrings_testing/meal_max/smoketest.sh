#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Song Management
#
##########################################################

clear_catalog() {
  echo "Clearing the playlist..."
  curl -s -X DELETE "$BASE_URL/clear-catalog" | grep -q '"status": "success"'
}


create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal: ($meal, $cuisine, $price, $difficulty)"
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add Meal."
    exit 1
  fi
}

delete_meal() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  #echo $?
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_combatants() {
  echo "Getting all meals in the catalog..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get combatants."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name (Meal: '$meal', Cuisine: '$cuisine', Price: $price)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name?meal=$(echo $meal | sed 's/ /%20/g')&Cuisine=$(echo $cuisine | sed 's/ /%20/g')&price=$price")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    exit 1
  fi
}


############################################################
#
# Playlist Management
#
############################################################

add_song_to_playlist() {
  artist=$1
  title=$2
  year=$3

  echo "Adding song to playlist: $artist - $title ($year)..."
  response=$(curl -s -X POST "$BASE_URL/add-song-to-playlist" \
    -H "Content-Type: application/json" \
    -d "{\"artist\":\"$artist\", \"title\":\"$title\", \"year\":$year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song added to playlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add song to playlist."
    exit 1
  fi
}


clear_playlist() {
  echo "Clearing playlist..."
  response=$(curl -s -X POST "$BASE_URL/clear-playlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Playlist cleared successfully."
  else
    echo "Failed to clear playlist."
    exit 1
  fi
}


############################################################
#
# Play Playlist
#
############################################################

play_current_song() {
  echo "Playing current song..."
  response=$(curl -s -X POST "$BASE_URL/play-current-song")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current song is now playing."
  else
    echo "Failed to play current song."
    exit 1
  fi
}

rewind_playlist() {
  echo "Rewinding playlist..."
  response=$(curl -s -X POST "$BASE_URL/rewind-playlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Playlist rewound successfully."
  else
    echo "Failed to rewind playlist."
    exit 1
  fi
}

get_all_songs_from_playlist() {
  echo "Retrieving all songs from playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-songs-from-playlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All songs retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Songs JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all songs from playlist."
    exit 1
  fi
}

get_song_from_playlist_by_track_number() {
  track_number=$1
  echo "Retrieving song by track number ($track_number)..."
  response=$(curl -s -X GET "$BASE_URL/get-song-from-playlist-by-track-number/$track_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Song retrieved successfully by track number."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve song by track number."
    exit 1
  fi
}

get_current_song() {
  echo "Retrieving current song..."
  response=$(curl -s -X GET "$BASE_URL/get-current-song")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current song retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Current Song JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve current song."
    exit 1
  fi
}


######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by play count
get_leaderboard() {
  echo "Getting  leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort_by=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by play count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get song leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Clear the catalog
clear_catalog

# Create songs
#create_meal "Spaghetti" "Italian" 12.5 "MED" 
create_meal "Pasta" "Italian" 20 "LOW" 
create_meal "Burger" "American" 13 "HIGH" 
create_meal "Sushi" "Japanese" 15 "LOW" 
create_meal "Hummus" "Arabic" 5 "MED" 

delete_meal 1
#delete_meal 2
#delete_meal 3
#delete_meal 4
#delete_meal 5
get_combatants
get_leaderboard

get_meal_by_id 2
get_meal_by_name "Pizza" "Italian" 12.5
#get_random_song

clear_playlist

add_song_to_playlist "The Rolling Stones" "Paint It Black" 1966
add_song_to_playlist "Queen" "Bohemian Rhapsody" 1975
add_song_to_playlist "Led Zeppelin" "Stairway to Heaven" 1971
add_song_to_playlist "The Beatles" "Let It Be" 1970

remove_song_from_playlist "The Beatles" "Let It Be" 1970
remove_song_by_track_number 2

get_all_songs_from_playlist

add_song_to_playlist "Queen" "Bohemian Rhapsody" 1975
add_song_to_playlist "The Beatles" "Let It Be" 1970

move_song_to_beginning "The Beatles" "Let It Be" 1970
move_song_to_end "Queen" "Bohemian Rhapsody" 1975
move_song_to_track_number "Led Zeppelin" "Stairway to Heaven" 1971 2
swap_songs_in_playlist 1 2

get_all_songs_from_playlist
get_song_from_playlist_by_track_number 1

get_playlist_length_duration

play_current_song
rewind_playlist

play_entire_playlist
play_current_song
play_rest_of_playlist

get_song_leaderboard

echo "All tests passed successfully!"