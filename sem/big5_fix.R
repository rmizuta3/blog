library(lavaan)
library(psych)
library(semTools)
library(semPlot)
library(gplots)

setwd("/Users/rmizuta/Documents/neta/lavaan") 

#https://www.kaggle.com/tunguz/big-five-personality-test
df=read.csv("data-final.csv",sep='\t',na.strings="NULL")

#使用変数
col=c("EXT1","EXT2","EXT3","EXT4","EXT5","EXT6","EXT7","EXT8","EXT9","EXT10", 
      "EST1","EST2","EST3","EST4","EST5","EST6","EST7","EST8","EST9","EST10", 
      "AGR1","AGR2","AGR3","AGR4","AGR5","AGR6","AGR7","AGR8","AGR9","AGR10",
      "CSN1","CSN2","CSN3","CSN4","CSN5","CSN6","CSN7","CSN8","CSN9","CSN10",
      "OPN1","OPN2","OPN3","OPN4","OPN5","OPN6","OPN7","OPN8","OPN9","OPN10",
      "testelapse","introelapse","endelapse"
)

xs<-df[,col]

#0,欠損処理
xs[xs == 0] <- NA
xs <- na.omit(xs)

#外れ値処理
xs=xs[xs$testelapse < 1000, ]
xs=xs[xs$introelapse < 1000, ]
xs=xs[xs$endelapse < 1000, ]

#log化
xs[,"testelapse"] <- log(xs$testelapse+1)
xs[,"introelapse"] <- log(xs$introelapse+1)
xs[,"endelapse"] <- log(xs$endelapse+1)

#変更前
model <- '
  # measurement model
    EXT =~ EXT1+EXT2+EXT3+EXT4+EXT5+EXT6+EXT7+EXT8+EXT9+EXT10
    EST =~ EST1+EST2+EST3+EST4+EST5+EST6+EST7+EST8+EST9+EST10
    AGR =~ AGR1+AGR2+AGR3+AGR4+AGR5+AGR6+AGR7+AGR8+AGR9+AGR10
    CSN =~ CSN1+CSN2+CSN3+CSN4+CSN5+CSN6+CSN7+CSN8+CSN9+CSN10
    OPN =~ OPN1+OPN2+OPN3+OPN4+OPN5+OPN6+OPN7+OPN8+OPN9+OPN10
    ELP =~ testelapse+introelapse+endelapse
  # regressions
    ELP ~ EXT+EST+AGR+CSN+OPN
'
fit <- sem(model, data=xs)
summary(fit, fit.measures=TRUE, standardized=TRUE)

#変更後
model <- '
  # measurement model
    EXT =~ EXT2+EXT4+EXT5+EXT7+EXT10
    EST =~ EST6+EST7+EST8
    AGR =~ AGR4+AGR5+AGR7+AGR9
    CSN =~ CSN1+CSN5
    OPN =~ OPN5+OPN10
    ELP =~ testelapse+introelapse+endelapse
  # regressions
    ELP ~ EXT+EST+AGR+CSN+OPN
'
#fit <- cfa(model, data=xs, estimator="ML")
fit <- sem(model, data=xs)
summary(fit, fit.measures=TRUE, standardized=TRUE)

png("graph.png", width=1000, height=800)
semPaths(object=fit, whatLabels="stand",exoVar = FALSE)
dev.off()
