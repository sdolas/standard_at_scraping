librarian::shelf("RSQLite", "ggplot2", "tidyr", "purrr", "dplyr", "lubridate", "tidytext", "stringr", "tidyquant", "patchwork")

Sys.setlocale(category = "LC_TIME", locale = "German")
setwd("C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping")
load("sentiws.RData")

# lade Daten
db <- "C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping\\article_data.db" # speichere pfad zur Datenbank
con <- dbConnect(drv=RSQLite::SQLite(), dbname=db) # Verbinde mit der Datenbank
tables <- dbListTables(con) # speichere alle Tabellen der Datenbank
tables <- tables[tables != "sqlite_sequence"] # entferne sqlite_sequence (beinhaltet tabelleninformation)
data <- dbGetQuery(conn=con, statement=paste0("SELECT * FROM '", tables[[1]], "'"))
data$pubdate <- as.Date(data$pubdate)
df <- data

# REGEX FILTERN
regex_list <- c("ÖVP", "Österreichische Volkspartei", "Volkspartei")
filtered_df <- df[grep(paste(regex_list, collapse = "|"), df$body),]

# SENTIMENT ANALYSE
# Funktion, die die Sentiment-Analyse für jeden Artikel durchführt
sentiment_analysis <- function(article_text) {
  data.frame(body=article_text)  |> 
    unnest_tokens(word, body)  |> 
    inner_join(sentiws)  |> 
    summarize(sentiment = sum(value)) |> 
    pull(sentiment)
}

# führe die Analyse für jeden Artikel durch
suppressMessages(
  filtered_df <- filtered_df |> 
    mutate(SentAna = purrr::map_chr(body, sentiment_analysis))
)

# reduziere die kicker auf n kicker + "sonstiges"
tmp <- filtered_df |> group_by(kicker) |> summarise(n = n())
topkicker <- tmp[order(tmp$n, decreasing = T),] |> head(10)
filtered_df$new_kicker <- ifelse(filtered_df$kicker %in% topkicker$kicker, filtered_df$kicker, "sonstiges")

# plotdata erstellen
filtered_df$SentAna<-filtered_df$SentAna |> as.numeric()
pltdata <- filtered_df |>
  filter(new_kicker != "sonstiges") |>
  group_by(pubdate, new_kicker) |>
  summarise(n = sum(n()), 
            percentage = n / sum(n), 
            sum_sentiment = sum(SentAna)) |>
  ungroup() |> 
  mutate(sentiment = ifelse(sum_sentiment > max(c(quantile(sum_sentiment, 0.95), 1)), "positiv", 
                            ifelse(sum_sentiment < min(c(quantile(sum_sentiment, 0.05),-1)), "negativ", "neutral")))

# PLOT
g <- ggplot(pltdata, aes(x=pubdate, y=new_kicker, group=sentiment, fill=sentiment))
g + geom_tile()+ 
  scale_x_date(date_breaks = "1 month", date_labels = "%b-%Y")+
  theme(axis.text.x = element_text(angle = 60, hjust = 1))+
  scale_fill_manual(values = c("positiv" = "green", "negativ" = "red", "neutral" = "grey"))
