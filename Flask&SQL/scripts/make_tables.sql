#make_tables.sql

DROP TABLE IF EXISTS `orderDetails`;
DROP TABLE IF EXISTS `supplierPhones`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `suppliers`;
DROP TABLE IF EXISTS `parts`;

CREATE TABLE `parts`
(
    `partID` int NOT NULL,
    `price` DOUBLE(10, 2),
    `description` VARCHAR(50),
    PRIMARY KEY (`partID`)
);

CREATE TABLE `suppliers`
(
    `supplierID` int NOT NULL,
    `name` VARCHAR(30),
    `email` VARCHAR(50),
    PRIMARY KEY (`supplierID`)
);

CREATE TABLE `orders`
(
    `orderID` int NOT NULL AUTO_INCREMENT,
    `date` VARCHAR(10),
    `supplierID` int NOT NULL,
    PRIMARY KEY (`orderID`),
    FOREIGN KEY (`supplierID`) REFERENCES `suppliers` (`supplierID`)
);

CREATE TABLE `supplierPhones`
(
    `telNumber` VARCHAR(20) NOT NULL,
    `supplierID` int NOT NULL,
    PRIMARY KEY (`telNumber`),
    FOREIGN KEY (`supplierID`) REFERENCES `suppliers` (`supplierID`)
);

CREATE TABLE `orderDetails`
(
    `orderID` int NOT NULL AUTO_INCREMENT,
    `partID` int NOT NULL,
    `qty` int,
    PRIMARY KEY (`orderID`, `partID`),
    FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`),
    FOREIGN KEY (`partID`) REFERENCES `parts` (`partID`)
);