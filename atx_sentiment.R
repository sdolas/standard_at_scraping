librarian::shelf("RSQLite", "ggplot2", "tidyr", "purrr", "dplyr", "lubridate", "tidytext", "stringr", "tidyquant", "patchwork")

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
df$boerse = 0
df$boerse[str_detect(df$body, "\\bBörse\\b|Aktien\\b|Anleihen\\b|Kapitalmarkt\\b|ATX")] <- 1

# filtere nur artikel, wo genau eine Partei vorkommt
df <- df  |> filter(boerse == 1)

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

# füge Börsenkurse hinzu
atx <- tq_get("^ATX", get = "stock.prices", from = " 1999-01-01")
df <- inner_join(df, atx, by=c("pubdate"="date"))

# reduziere die kicker auf n kicker + "sonstiges"
tmp <- df |> group_by(kicker) |> summarise(n = n())
topkicker <- tmp[order(tmp$n, decreasing = T),] |> head(5)
df$new_kicker <- ifelse(df$kicker %in% topkicker$kicker, df$kicker, "sonstiges")

# gruppiere
df$SentAna <- df$SentAna |> as.numeric()
pltdata <- df |>
  group_by(pubdate, new_kicker) |>
  summarise(n = sum(n()), 
            percentage = n / sum(n), 
            sum_sentiment = sum(SentAna),
            kurs=close) |>
  ungroup() |> 
  mutate(sentiment = ifelse(sum_sentiment > max(c(quantile(sum_sentiment, 0.95), 1)), "positive", 
                            ifelse(sum_sentiment < min(c(quantile(sum_sentiment, 0.05),-1)), "negative", "neutral")))


# plotte
pltdata <- na.omit(pltdata)
# Plot 1 erstellen
p1 <- ggplot(pltdata, aes(x = pubdate, y=kurs)) + 
  geom_line(aes()) +
  theme_classic()+
  theme(axis.text.x = element_text(angle = 60, hjust = 1))+
  labs(title = "ATX-Kurse und Artikel mit Börsenbezug", x = "", y = "ATX-Index")

# Plot 2 erstellen
p2 <- ggplot(pltdata, aes(x = pubdate, y = new_kicker, group=sentiment, fill=sentiment)) + 
  geom_tile()+
  theme_classic()+
  scale_x_date(date_breaks = "3 month", date_labels = "%b-%Y")+
  scale_fill_manual(values = c("positive" = "green", "negative" = "red", "neutral" = "lightgrey"))+
  theme(axis.text.x = element_text(angle = 60, hjust = 1))+
  labs(x = "Datum", y = "Kategorie")


# Plots kombinieren und ausrichten
(p1 + theme(axis.title.x=element_blank(), axis.text.x=element_blank(), axis.ticks.x=element_blank())) /
  p2 + plot_layout(guides = "auto") + 
  theme(axis.title.x=element_text(size=14, face="bold"), axis.text.x=element_text(size=12)) + 
  plot_annotation(tag_levels = NULL)

