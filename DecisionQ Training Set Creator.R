######################################
# DecisionQ Model Creation Task
######################################

# Supporting code for creating the prediction model.
# See "DecisionQ Regression Model Creator.R" to view the total output of the code

library(tidyverse)
library(rvest)
library(stringr)
library(dplyr)
library(readr)

wd <- getwd()

Scraper <- function(url) {
  ####################################
  # Input: url (the url of the webpage to be scraped)
  # Output: data (the raw data from the webpage)
  # Description: Scrapes the webpage from the given url and outputs 
  #              data to be put into a dataframe
  ####################################
  webpage <- read_html(url)
  data_html <- html_nodes(webpage, "tr")
  data <- html_text(data_html)
  
  for (a in 1:length(data)) {
    data[a] <- gsub("\n", ";", data[a]) }
  
  for (a in 1:length(data)) {
    data[a] <- gsub("\\*", ";", data[a]) }
  
  for (a in 1:length(data)) {
    data[a] <- gsub("\\^", ";", data[a]) }
  
  for (a in 1:length(data)) {
    data[a] <- gsub("\\#", ";", data[a]) }
    
    return(data)

}

Create.Dataframe <- function(data) {
  ####################################
  # Input: data (the raw data from a scraped webpage)
  # Output: df1 (a dataframe containing the raw data)
  # Description: Creates a dataframe of the movie data separated
  #              into respective columns
  ####################################
  df <- data.frame(data)
 
  df1 <- separate(df, col = "data", into = c("Title", "Opening Date", "Closing Date",
                                            "Gross Total", "Gross Opening", "Theaters Opening",
                                            "Theaters Widest", "1st Week Percentage",
                                            "Per Theater Attendance", "Distributor"), sep = c(";{2,}"), remove = TRUE, extra = "drop")
  
  return(df1)
}

Add.To.Dataframe <- function(df, new_df) {
  ####################################
  # Input: df (the pre-existing dataframe)
  #        new_df (the dataframe to be added to the existing dataframe)
  # Output: added_df (the combined dataframes)
  # Description: Takes two dataframes and merges them based on column names
  ####################################
  added_df <- dplyr::bind_rows(df, new_df)
  
  return(added_df)
}
  
Clean.Dataframe <- function(df) {
  ####################################
  # Input: df (the dataframe to be cleaned)
  # Output: df (the cleaned dataframe)
  # Description: Takes a dataframe and gets rid of extra punctuation in columns
  ####################################
  df <- df[complete.cases(df),]
     
  for (a in 1:length(df$Title)) {
    df$Title[a] <- gsub(";", " ", df$Title[a]) }
     
  for (a in 1:length(df$Distributor)) {
    df$Distributor[a] <- gsub(";", " ", df$Distributor[a]) }
     
  return(df)
}

More.Pages <- function(url) {
  ####################################
  # Input: url (the url of the page currently being scraped)
  # Output: boolean
  # Description: Outputs TRUE if there are more pages to be scraped for
  #              the starting movie letter, and FALSE if not
  ####################################
  webpage <- read_html(url)
  more_page <- html_text(html_nodes(webpage, "a"))
  
  return("more" %in% more_page)
}
     
A.Count <- function() {
  ####################################
  # Input: N/A
  # Output: a_count (The number of pages to be scraped for the letter "A")
  # Description: Determines how many pages are to be scraped for the given letter
  ####################################
  a_url <- "http://www.boxofficeguru.com/a.htm"
  a_count <- 1

  while (More.Pages(a_url)) {
    a_count <- a_count + 1
    a_url <- paste("http://www.boxofficeguru.com/a", a_count, ".htm", sep = "")
  }
  
  return(a_count)
}

B.Count <- function() {
  ####################################
  # Input: N/A
  # Output: b_count (The number of pages to be scraped for the letter "B")
  # Description: Determines how many pages are to be scraped for the given letter
  ####################################
  b_url <- "http://www.boxofficeguru.com/b.htm"
  b_count <- 1
  
  while (More.Pages(b_url)) {
    b_count <- b_count + 1
    b_url <- paste("http://www.boxofficeguru.com/b", b_count, ".htm", sep = "")
  }
  
  return(b_count)
}

C.Count <- function() {
  ####################################
  # Input: N/A
  # Output: c_count (The number of pages to be scraped for the letter "C")
  # Description: Determines how many pages are to be scraped for the given letter
  ####################################
  c_url <- "http://www.boxofficeguru.com/c.htm"
  c_count <- 1
  
  while (More.Pages(c_url)) {
    c_count <- c_count + 1
    c_url <- paste("http://www.boxofficeguru.com/c", c_count, ".htm", sep = "")
  }
  return(c_count)
}

D.Count <- function() {
  ####################################
  # Input: N/A
  # Output: d_count (The number of pages to be scraped for the letter "D")
  # Description: Determines how many pages are to be scraped for the given letter
  ####################################
  d_url <- "http://www.boxofficeguru.com/d.htm"
  d_count <- 1
  
  while (More.Pages(d_url)) {
    d_count <- d_count + 1
    d_url <- paste("http://www.boxofficeguru.com/d", d_count, ".htm", sep = "")
  }
  return(d_count)
}

Make.A.Dataframe <- function(initial_url) {
  ####################################
  # Input: initial_url (the first url given)
  # Output: df (The dataframe of movies starting with "A")
  # Description: Creates the dataframe for movies starting with the given letter
  ####################################
  a_count <- A.Count()
  data <- Scraper(initial_url)
  df <- Create.Dataframe(data)
  
  for (i in 2:a_count) {
    current_url <- paste("http://www.boxofficeguru.com/a", a_count, ".htm", sep = "")
    data1 <- Scraper(current_url)
    df1 <- Create.Dataframe(data1)
    df <- Add.To.Dataframe(df, df1)
  }
  
  return(df)
}

Make.B.Dataframe <- function(initial_url) {
  ####################################
  # Input: initial_url (the first url given)
  # Output: df (The dataframe of movies starting with "B")
  # Description: Creates the dataframe for movies starting with the given letter
  ####################################
  b_count <- B.Count()
  data <- Scraper(initial_url)
  df <- Create.Dataframe(data)
  
  for (i in 2:b_count) {
    current_url <- paste("http://www.boxofficeguru.com/b", b_count, ".htm", sep = "")
    data1 <- Scraper(current_url)
    df1 <- Create.Dataframe(data1)
    df <- Add.To.Dataframe(df, df1)
  }
  
  return(df)
}

Make.C.Dataframe <- function(initial_url) {
  ####################################
  # Input: initial_url (the first url given)
  # Output: df (The dataframe of movies starting with "C")
  # Description: Creates the dataframe for movies starting with the given letter
  ####################################
  c_count <- C.Count()
  data <- Scraper(initial_url)
  df <- Create.Dataframe(data)
  
  for (i in 2:c_count) {
    current_url <- paste("http://www.boxofficeguru.com/c", c_count, ".htm", sep = "")
    data1 <- Scraper(current_url)
    df1 <- Create.Dataframe(data1)
    df <- Add.To.Dataframe(df, df1)
  }
  
  return(df)
}

Make.D.Dataframe <- function() {
  ####################################
  # Input: initial_url (the first url given)
  # Output: df (The dataframe of movies starting with "D")
  # Description: Creates the dataframe for movies starting with the given letter
  ####################################
  initial_url <- "http://www.boxofficeguru.com/d.htm"
  d_count <- D.Count()
  data <- Scraper(initial_url)
  df <- Create.Dataframe(data)
  
  for (i in 2:d_count) {
    current_url <- paste("http://www.boxofficeguru.com/d", d_count, ".htm", sep = "")
    data1 <- Scraper(current_url)
    df1 <- Create.Dataframe(data1)
    df <- Add.To.Dataframe(df, df1)
  }
  df <- Clean.Dataframe(df)
  write.csv(df, "d.df.csv", row.names = FALSE)
  return(df)
}

Create_Training_Set <- function() {
  ####################################
  # Input: N/A
  # Output: clean_df_final (the final cleaned dataframe for letters A, B, and C)
  # Description: Uses other functions to create he training set
  ####################################
  a_url <- "http://www.boxofficeguru.com/a.htm"
  b_url <- "http://www.boxofficeguru.com/b.htm"
  c_url <- "http://www.boxofficeguru.com/c.htm"
  
  a.df <- Make.A.Dataframe(a_url)
  b.df <- Make.B.Dataframe(b_url)
  c.df <- Make.C.Dataframe(c_url)
  
  total_df <- dplyr::bind_rows(a.df, b.df, c.df)
  clean_df_final <- Clean.Dataframe(total_df)
  write.csv(clean_df_final, "abcmovies.csv", row.names = FALSE)
  return(clean_df_final)
}
