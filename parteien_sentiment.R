librarian::shelf("RSQLite", "ggplot2", "tidyr", "purrr", "dplyr", "lubridate", "tidytext", "stringr")

setwd("C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping")
load("sentiws.RData")

# speichere pfad zur Datenbank
db <- "C:\\Users\\user00\\Documents\\GitHub\\standard_at_scraping\\article_data.db"

## Verbinde mit der Datenbank
con <- dbConnect(drv=RSQLite::SQLite(), dbname=db)

## speichere alle Tabellen der Datenbank
tables <- dbListTables(con)

## entferne sqlite_sequence (beinhaltet tabelleninformation)
tables <- tables[tables != "sqlite_sequence"]

# lade daten
data <- dbGetQuery(conn=con, statement=paste0("SELECT * FROM '", tables[[1]], "'"))
data$pubdate <- as.Date(data$pubdate)

df <- data

df$oevp = 0
df$spoe = 0
df$fpoe = 0
df$gruene = 0
df$oevp[str_detect(df$body, "\\bÖVP\\b|Österreichische Volkspartei")] <- 1
df$spoe[str_detect(df$body, "\\bSPÖ\\b|Sozialdemokratische Partei Österreichs")] <- 1
df$fpoe[str_detect(df$body, "\\bFPÖ\\b|Freiheitliche Partei Österreichs")] <- 1
df$gruene[str_detect(df$body, "\\bGrüne\\b|Die Grünen")] <- 1

df <- df  |> 
  filter((oevp + spoe + fpoe + gruene) == 1)

df <- df |> 
  mutate(Partei = case_when(oevp == 1 ~ "ÖVP",
                            spoe == 1 ~ "SPÖ",
                            fpoe == 1 ~ "FPÖ",
                            gruene == 1 ~ "Grüne"))  |> 
  select(!c(oevp, spoe, fpoe, gruene))


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
  df <- df |> 
    mutate(SentAna = purrr::map_chr(body, sentiment_analysis))
)


# group by
df$SentAna <- df$SentAna |> as.numeric()
pltdata <- df |>
  group_by(pubdate, Partei) |>
  summarise(n = sum(n()), 
            percentage = n / sum(n), 
            sum_sentiment = sum(SentAna)) |>
  ungroup() |> 
  mutate(sentiment = ifelse(sum_sentiment > 0, "positive", 
                            ifelse(sum_sentiment < 0, "negative", "neutral")))





g <- ggplot(pltdata, aes(x=pubdate, y=Partei, group=sentiment, fill=sentiment))
g + geom_tile()+ 
  scale_x_date(date_breaks = "1 month", date_labels = "%b-%Y")+
  theme(axis.text.x = element_text(angle = 60, hjust = 1))+
  scale_fill_manual(values = c("positive" = "green", "negative" = "red", "neutral" = "grey"))
