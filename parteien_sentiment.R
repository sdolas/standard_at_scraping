librarian::shelf("RSQLite", "ggplot2", "tidyr", "purrr", "dplyr", "lubridate", "tidytext", "stringr")

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

# erstelle dummy-variablen 
df$oevp = 0
df$spoe = 0
df$fpoe = 0
df$gruene = 0
df$lif = 0
df$kpoe = 0
df$cpoe = 0
df$oevp[str_detect(df$body, "\\bÖVP\\b|Österreichische Volkspartei")] <- 1
df$spoe[str_detect(df$body, "\\bSPÖ\\b|Sozialdemokratische Partei Österreichs")] <- 1
df$fpoe[str_detect(df$body, "\\bFPÖ\\b|Freiheitliche Partei Österreichs")] <- 1
df$gruene[str_detect(df$body, "\\bGrüne\\b|Die Grünen")] <- 1
df$lif[str_detect(df$body, "\\bLIF\\b|Liberales Forum")] <- 1
df$kpoe[str_detect(df$body, "\\bKPÖ\\b|Kommunistische Partei")] <- 1

# filtere nur artikel, wo genau eine Partei vorkommt
df <- df  |> 
  filter((oevp + spoe + fpoe + gruene + lif + kpoe) == 1)

# ersetze dummies durch kategoriale variable
df <- df |> 
  mutate(Partei = case_when(oevp == 1 ~ "ÖVP",
                            spoe == 1 ~ "SPÖ",
                            fpoe == 1 ~ "FPÖ",
                            gruene == 1 ~ "Grüne",
                            lif == 1 ~ "Liberales Forum",
                            kpoe == 1 ~ "KPÖ"))  |> 
  select(!c(oevp, spoe, fpoe, gruene, lif, kpoe))

## SENTIMENT ANALYSE
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

# gruppiere
df$SentAna <- df$SentAna |> as.numeric()
pltdata <- df |>
  group_by(pubdate,Partei) |>
  summarise(n = sum(n()), 
            percentage = n / sum(n), 
            sum_sentiment = sum(SentAna)) |>
  ungroup() |> 
  mutate(sentiment = ifelse(sum_sentiment > max(c(quantile(sum_sentiment, 0.95), 1)), "positive", 
                            ifelse(sum_sentiment < min(c(quantile(sum_sentiment, 0.05),-1)), "negative", "neutral")))

# plotte
g <- ggplot(pltdata, aes(x=pubdate, y=Partei, group=sentiment, fill=sentiment))
g + geom_tile()+ 
  scale_x_date(date_breaks = "1 month", date_labels = "%b-%Y")+
  theme_classic()+
  theme(axis.text.x = element_text(angle = 60, hjust = 1))+
  scale_fill_manual(values = c("positive" = "green", "negative" = "red", "neutral" = "lightgrey"))


  
