### Displays the parameter sweeps, adjusting food and fuel prices

setwd("~/projects/water/fivecounties")

do.combine <- F
do.seven <- F

if (do.combine) {
    prices1 <- read.csv("prices1.csv")
    prices2 <- read.csv("prices2.csv")

    data <- prices[0,]

    for (ii in 1:nrow(prices1)) {
        if (prices1$objective[ii] > prices2$objective[ii])
            data <- rbind(data, prices1[ii,])
        else
            data <- rbind(data, prices2[ii,])
    }
}

data <- read.csv("prices.csv")

data$betamean <- NA
data$phimean <- NA
data$lambdaAmean <- NA
data$sigmaAmean <- NA
data$lambdaCmean <- NA
data$sigmaCmean <- NA
data$betansd <- NA
data$phinsd <- NA
data$lambdaAnsd <- NA
data$sigmaAnsd <- NA
data$lambdaCnsd <- NA
data$sigmaCnsd <- NA

for (ii in 1:nrow(data)) {
    betas <- as.numeric(data[ii, c('beta1', 'beta2', 'beta3', 'beta4', 'beta5')])
    phis <- as.numeric(data[ii, c('phi1', 'phi2', 'phi3', 'phi4', 'phi5')])
    lambda_As <- as.numeric(data[ii, c('lambda_A1', 'lambda_A2', 'lambda_A3', 'lambda_A4', 'lambda_A5')])
    sigma_As <- as.numeric(data[ii, c('sigma_A1', 'sigma_A2', 'sigma_A3', 'sigma_A4', 'sigma_A5')])
    lambda_Cs <- as.numeric(data[ii, c('lambda_C1', 'lambda_C2', 'lambda_C3', 'lambda_C4', 'lambda_C5')])
    sigma_Cs <- as.numeric(data[ii, c('sigma_C1', 'sigma_C2', 'sigma_C3', 'sigma_C4', 'sigma_C5')])

    data$betamean[ii] <- mean(betas)
    data$betansd[ii] <- ifelse(mean(betas) == 0, 0, sd(betas) / mean(betas))
    data$phimean[ii] <- mean(phis)
    data$phinsd[ii] <- ifelse(mean(phis) == 0, 0, sd(phis) / mean(phis))
    data$lambdaAmean[ii] <- mean(lambda_As)
    data$lambdaAnsd[ii] <- ifelse(mean(lambda_As) == 0, 0, sd(lambda_As) / mean(lambda_As))
    data$sigmaAmean[ii] <- mean(sigma_As)
    data$sigmaAnsd[ii] <- ifelse(mean(sigma_As) == 0, 0, sd(sigma_As) / mean(sigma_As))
    data$lambdaCmean[ii] <- mean(lambda_Cs)
    data$lambdaCnsd[ii] <- ifelse(mean(lambda_Cs) == 0, 0, sd(lambda_Cs) / mean(lambda_Cs))
    data$sigmaCmean[ii] <- mean(sigma_Cs)
    data$sigmaCnsd[ii] <- ifelse(mean(sigma_Cs) == 0, 0, sd(sigma_Cs) / mean(sigma_Cs))
}

library(ggplot2)

if (do.seven) {
    data$rpE <- NA
    data$rpE[data$p_E == .1] <- 1
    data$rpE[data$p_E == .2] <- 2
    data$rpE[data$p_E == .5] <- 3
    data$rpE[data$p_E == 1] <- 4
    data$rpE[data$p_E == 2] <- 5
    data$rpE[data$p_E == 5] <- 6
    data$rpE[data$p_E == 10] <- 7

    data$rpF <- NA
    data$rpF[data$p_F == .1] <- 1
    data$rpF[data$p_F == .2] <- 2
    data$rpF[data$p_F == .5] <- 3
    data$rpF[data$p_F == 1] <- 4
    data$rpF[data$p_F == 2] <- 5
    data$rpF[data$p_F == 5] <- 6
    data$rpF[data$p_F == 10] <- 7

    data2 <- data[data$objective > -1e9,]
}

limits <- quantile(data$objective, probs=c(.01, .99))
data2 <- data[data$objective > limits[1] & data$objective < limits[2],]
##data2 <- data[data$objective > 0,]

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=objective)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

#
ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=betamean)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0)) +
            xlab("Price of Fuel") + ylab("Price of Food") +
                ggtitle("Mean fraction of agriculture for biofuel")

# Have no explanation for...
ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=betansd)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0)) +
            xlab("Price of Fuel") + ylab("Price of Food") +
                ggtitle("Variation in fraction of agriculture for biofuel")

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=phimean)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0)) +
            xlab("Price of Fuel") + ylab("Price of Food") +
                ggtitle("Mean fuel purchased annually")

#
ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=phinsd)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0)) +
            xlab("Price of Fuel") + ylab("Price of Food") +
                ggtitle("Variation in fuel purchased annually")

#
ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=lambdaAmean)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0)) +
            xlab("Price of Fuel") + ylab("Price of Food") +
                ggtitle("Mean water to agriculture")

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=lambdaAnsd)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=sigmaAmean)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=sigmaAnsd)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=lambdaCmean)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=lambdaCnsd)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=sigmaCmean)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

ggplot(data2, aes(x=p_E, y=p_F)) +
    geom_tile(aes(fill=sigmaCnsd)) +
        scale_x_log10(expand=c(0, 0)) + scale_y_log10(expand=c(0, 0))

