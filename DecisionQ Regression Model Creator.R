######################################
# DecisionQ Regression Model Creator
######################################

################ READ ################
# First, run the two individual functions in this script.  Then, uncomment and 
# run the following two commands:
#
# predict_df <- Run_Prediction()
# regression <- Fit_Evaluation(predict_df)
#
# The first command will give you a dataframe showing the data for all the movies
# in the dataset beginning with "D" along with the predictions for the total gross
# revenue of each movie.
# The second command will give the summary of a regression model evaluating the 
# relationship between the actual total revenue and the predicted total revenue of 
# movies beginning with "D".
#
# NOTE: 1. The script "DecisionQ Training Set Creator.R" must be downloaded and in the
#       same working directory before running
#       2. Edit the working directory just below to match your current directory
######################################

# Edit to match working directory before running
wd <- paste("/Users/Kyle/Documents/DecisionQ Coding Exercise/DecisionQ Model Creation Task")

Run_Prediction <- function() {
  ####################################
  # Input: N/A
  # Output: d.df (the complete dataframe of movies beginning with "D" with
  #               predicted total gross revenue values in the last column)
  # Description: Creates a dataframe of movies beginning with "D" to compare
  #              between the actual total revenue and the predicted total revenue
  #              by running a stepwise regression model
  #
  # NOTE: Edit your working directory to the directory the scripts are saved in
  ####################################
  library(MASS)

  source(paste(wd, "/DecisionQ Training Set Creator.R", sep = ""))
  
  abcmovies <- Create_Training_Set()
  abcmovies <- read_csv(paste(wd, "/abcmovies.csv", sep = ""))
  
  d.df <- Make.D.Dataframe()
  d.df <- read_csv(paste(wd, "/d.df.csv", sep = ""))
  
  names(abcmovies) <- c("Title", "Opening.Date", "Closing.Date",
                        "Gross.Total", "Gross.Opening", "Theaters.Opening",
                        "Theaters.Widest", "First.Week.Percentage",
                        "Per.Theater.Attendance", "Distributor")
  
  names(d.df) <- c("Title", "Opening.Date", "Closing.Date",
                   "Gross.Total", "Gross.Opening", "Theaters.Opening",
                   "Theaters.Widest", "First.Week.Percentage",
                   "Per.Theater.Attendance", "Distributor")
  
  d.df$Predicted.Gross.Total <- NA
  
  lmMod <- lm(Gross.Total ~ Gross.Opening + Theaters.Opening +
            Theaters.Widest + First.Week.Percentage + Per.Theater.Attendance +
            Distributor, data = abcmovies)

  step <- stepAIC(lmMod, direction = "both")
  
  d.df$Predicted.Gross.Total <- predict(step, d.df)
  
  return(d.df)

}

Fit_Evaluation <- function(d.df) {
  ####################################
  # Input: N/A
  # Output: regression (the summary of the regression model)
  # Description: Returns the summary of the regression 
  #              evaluating the relationship between the actual 
  #              total revenue and the predicted total revenue
  ####################################
  regression <- summary(lm(Gross.Total ~ Predicted.Gross.Total, data = d.df))
  
  return(regression)
}

