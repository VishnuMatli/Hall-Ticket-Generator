-- Active: 1764577825488@@127.0.0.1@3306@hall_ticket_db_university
/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: hall_ticket_db_university
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-1+b1 from Debian

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `admin_users`
--

DROP TABLE IF EXISTS `admin_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `failed_attempts` int(11) DEFAULT 0,
  `is_locked` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_users`
--

LOCK TABLES `admin_users` WRITE;
/*!40000 ALTER TABLE `admin_users` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `admin_users` VALUES
(1,'admin','$2b$12$qQPTlztPXDzXeufjXtLeB.7MSQwJ4xIvYETvwNzKWFFBJ/OUl57re',0,0),
(2,'vishnu','$2b$12$OWTJWp7NORdvcULlWnDpI.1P0vr/BuTTdFb3x995v3zhgbeYrsfxC',0,0);
/*!40000 ALTER TABLE `admin_users` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `connection_logs`
--

DROP TABLE IF EXISTS `connection_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `connection_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT current_timestamp(),
  `ip_address` varchar(100) DEFAULT NULL,
  `device_name` varchar(255) DEFAULT NULL,
  `roll_number` varchar(50) DEFAULT NULL,
  `name` varchar(150) DEFAULT NULL,
  `semester` varchar(20) DEFAULT NULL,
  `hallticket_info` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_conn_lookup` (`roll_number`,`semester`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `connection_logs`
--

LOCK TABLES `connection_logs` WRITE;
/*!40000 ALTER TABLE `connection_logs` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `connection_logs` VALUES
(1,'2025-12-11 19:48:13','::1','Linux  – PC / Laptop (Chrome)','23691A3330','Yemmala Lekha Sree','III-II','Exam: Regular / June 2026, Dept: AI & ML, Sem: III-II, Reg: R23, Subjects: 23CSM110, 23CSM111, 23CSM112, PE-II, PE-III, 23CSM207, 23CSM208, 23ECE501, 23CSM801, 23MD3M01, 23MG3M01, 23ENG601'),
(2,'2025-12-12 17:42:13','::1','Linux  – PC / Laptop (Chrome)','23691A3330','Yemmala Lekha Sree','III-II','Exam: Regular / May 2026, Dept: AI & ML, Sem: III-II, Reg: R23, Subjects: 23CSM110, 23CSM111, 23CSM112, 23CSM405, 23CSM406, 23CSM207, 23CSM208, 23ECE501, 23CSM801, 23MD3M01, 23MG3M01, 23ENG601'),
(3,'2025-12-12 17:43:44','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSM110, 23CSM111, 23CSM112, 23CSM405, 23CSM406, 23CSM207, 23CSM208, 23ECE501, 23CSM801, 23MD3M01, 23MG3M01, 23ENG601'),
(4,'2025-12-12 17:45:12','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(5,'2025-12-13 19:14:58','2401:4900:97c4:887e:149e:6cff:fe31:7d26','Android 10 – K (Mobile Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(6,'2025-12-13 19:27:48','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / June 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(7,'2025-12-13 20:05:25','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / June 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(8,'2025-12-13 20:06:53','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / June 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(9,'2025-12-13 20:08:41','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / June 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(10,'2025-12-13 20:20:26','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(11,'2025-12-13 20:26:41','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / June 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(12,'2025-12-13 20:29:10','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(13,'2025-12-13 20:30:34','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(14,'2025-12-13 20:30:40','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(15,'2025-12-13 20:31:02','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(16,'2025-12-13 20:34:27','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(17,'2025-12-13 20:34:51','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(18,'2025-12-13 20:36:26','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(19,'2025-12-13 20:37:09','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(20,'2025-12-13 20:41:55','2401:4900:97c4:887e:149e:6cff:fe31:7d26','Android 10 – K (Mobile Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(21,'2025-12-13 20:43:37','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(22,'2025-12-13 20:44:34','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(23,'2025-12-13 20:45:03','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(24,'2025-12-13 20:45:33','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(25,'2025-12-13 20:46:31','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(26,'2025-12-13 20:48:18','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(27,'2025-12-13 20:48:54','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801'),
(28,'2025-12-13 20:50:04','::1','Linux  – PC / Laptop (Chrome)','24695A4006','MATLI VISHNU VARDHAN NAIDU','III-II','Exam: Regular / May 2026, Dept: Networks, Sem: III-II, Reg: R23, Subjects: 23CSN110, 23CSN111, 23CSN112, 23CSN401, 23CSN409, 23MG3M01, 23MD3M01, 23CSN207, 23CSN208, 23ENG601, 23ECE501, 23CSN801');
/*!40000 ALTER TABLE `connection_logs` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `departments` VALUES
(10,'AI'),
(2,'AI & ML'),
(3,'Civil'),
(8,'CST'),
(7,'Cyber Security'),
(9,'Data Science'),
(6,'ECE'),
(5,'EEE'),
(4,'Mechanical'),
(1,'Networks');
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `halltickets`
--

DROP TABLE IF EXISTS `halltickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `halltickets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roll_number` varchar(20) DEFAULT NULL,
  `exam_type` varchar(50) DEFAULT NULL,
  `exam_month` varchar(20) DEFAULT NULL,
  `exam_year` varchar(10) DEFAULT NULL,
  `generated_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Table structure for table `hallticket_verifications`

DROP TABLE IF EXISTS `hallticket_verifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `hallticket_verifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(64) NOT NULL,
  `roll_number` varchar(20) NOT NULL,
  `exam_type` varchar(50) NOT NULL,
  `exam_month` varchar(20) NOT NULL,
  `exam_year` varchar(10) NOT NULL,
  `generated_at` timestamp NULL DEFAULT current_timestamp(),
  `verified_at` datetime DEFAULT NULL,
  `status` enum('active','revoked') DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roll_number` varchar(20) NOT NULL,
  `exam_type` varchar(50) NOT NULL,
  `exam_month` varchar(20) NOT NULL,
  `exam_year` varchar(10) NOT NULL,
  `amount` int(11) NOT NULL,
  `status` varchar(20) DEFAULT 'created',
  `approval_status` varchar(20) DEFAULT 'pending',
  `razorpay_order_id` varchar(100) DEFAULT NULL,
  `razorpay_payment_id` varchar(100) DEFAULT NULL,
  `razorpay_signature` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `paid_at` datetime DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `approved_by` varchar(50) DEFAULT NULL,
  `approval_note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_payment_lookup` (`roll_number`,`exam_type`,`exam_month`,`exam_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `halltickets`
--

LOCK TABLES `halltickets` WRITE;
/*!40000 ALTER TABLE `halltickets` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `halltickets` VALUES
(1,'23691A3330','Regular','June','2026','2025-12-11 14:18:13'),
(2,'23691A3330','Regular','May','2026','2025-12-12 12:12:13'),
(3,'24695A4006','Regular','May','2026','2025-12-12 12:13:44'),
(4,'24695A4006','Regular','May','2026','2025-12-12 12:15:12'),
(5,'24695A4006','Regular','May','2026','2025-12-13 13:44:58'),
(6,'24695A4006','Regular','June','2026','2025-12-13 13:57:48'),
(7,'24695A4006','Regular','June','2026','2025-12-13 14:35:25'),
(8,'24695A4006','Regular','June','2026','2025-12-13 14:36:53'),
(9,'24695A4006','Regular','June','2026','2025-12-13 14:38:41'),
(10,'24695A4006','Regular','May','2026','2025-12-13 14:50:26'),
(11,'24695A4006','Regular','June','2026','2025-12-13 14:56:41'),
(12,'24695A4006','Regular','May','2026','2025-12-13 14:59:10'),
(13,'24695A4006','Regular','May','2026','2025-12-13 15:00:34'),
(14,'24695A4006','Regular','May','2026','2025-12-13 15:00:40'),
(15,'24695A4006','Regular','May','2026','2025-12-13 15:01:02'),
(16,'24695A4006','Regular','May','2026','2025-12-13 15:04:27'),
(17,'24695A4006','Regular','May','2026','2025-12-13 15:04:51'),
(18,'24695A4006','Regular','May','2026','2025-12-13 15:06:26'),
(19,'24695A4006','Regular','May','2026','2025-12-13 15:07:09'),
(20,'24695A4006','Regular','May','2026','2025-12-13 15:11:55'),
(21,'24695A4006','Regular','May','2026','2025-12-13 15:13:37'),
(22,'24695A4006','Regular','May','2026','2025-12-13 15:14:34'),
(23,'24695A4006','Regular','May','2026','2025-12-13 15:15:03'),
(24,'24695A4006','Regular','May','2026','2025-12-13 15:15:33'),
(25,'24695A4006','Regular','May','2026','2025-12-13 15:16:31'),
(26,'24695A4006','Regular','May','2026','2025-12-13 15:18:18'),
(27,'24695A4006','Regular','May','2026','2025-12-13 15:18:54'),
(28,'24695A4006','Regular','May','2026','2025-12-13 15:20:04');
/*!40000 ALTER TABLE `halltickets` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `regulations`
--

DROP TABLE IF EXISTS `regulations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `regulations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regulations`
--

LOCK TABLES `regulations` WRITE;
/*!40000 ALTER TABLE `regulations` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `regulations` VALUES
(3,'R19'),
(2,'R20'),
(1,'R23');
/*!40000 ALTER TABLE `regulations` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `semesters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semesters`
--

LOCK TABLES `semesters` WRITE;
/*!40000 ALTER TABLE `semesters` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `semesters` VALUES
(1,'I-I'),
(2,'I-II'),
(3,'II-I'),
(4,'II-II'),
(5,'III-I'),
(6,'III-II'),
(7,'IV-I'),
(8,'IV-II');
/*!40000 ALTER TABLE `semesters` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `roll_number` varchar(20) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `father_name` varchar(120) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `regulation` varchar(10) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `semester` varchar(10) DEFAULT NULL,
  `section` varchar(5) DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `mother_name` varchar(120) DEFAULT NULL,
  `caste` varchar(20) NOT NULL,
  `quota_type` varchar(20) DEFAULT 'CONVENER',
  `college_fee_total` int(11) DEFAULT 0,
  `college_fee_pending` int(11) DEFAULT 0,
  PRIMARY KEY (`roll_number`),
  KEY `idx_student_lookup` (`roll_number`,`dob`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roll_number` varchar(20) NOT NULL,
  `semester` varchar(10) NOT NULL,
  `percentage` decimal(5,2) NOT NULL,
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_attendance` (`roll_number`,`semester`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam_fee_rules`
--

DROP TABLE IF EXISTS `exam_fee_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_fee_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exam_type` varchar(50) NOT NULL,
  `min_backlogs` int(11) NOT NULL,
  `max_backlogs` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `students` VALUES
('23691A3330','YEMMALA LEKHA SREE','Yemmala Reddy Sekhar','2006-10-09','Female','9676512443','AI & ML','R23',3,'III-II','A','/home/vishnu/Desktop/university-version/uploads/23691A3330.jpg','B Jyothsna','BC-B'),
('23691A4002','PATNOOL MOHAMMED AFNAN','PATNOOL IRSHAD','2005-12-21','Male','7794090043','Networks','R23',3,'III-II','A',NULL,'test','BC-E'),
('23691A4003','MEKA ANUDEEP','test','2001-01-02','Male','9381549045','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4005','NOORBASHA MOHAMMED ASIF','test','2001-01-03','Male','7702788301','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4006','TELLA MEKALA BHANU PRAKASH YADAV','test','2001-01-04','Male','8919796917','Networks','R23',3,'III-II','A',NULL,'test','BC-D'),
('23691A4007','BILLA BHANU SANDHYA','test','2001-01-05','Female','9381361790','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4008','KAVALA BHARATH','test','2001-01-06','Male','8309385392','Networks','R23',3,'III-II','A',NULL,'test','SC'),
('23691A4009','MEKALA BHAVYA SREE','test','2005-12-30','Female','6303486795','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4010','DEVI REDDY CHAITANYA KUMAR REDDY','test','2001-01-08','Male','9391788898','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4011','TANAKANTI DEVENDRAREDDY','test','2001-01-09','Male','9347698116','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4012','SYED FARHAN','test','2001-01-10','Male','6302056860','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4013','MEKALA BOJJI GARI GANESH','test','2001-01-11','Male','6303372651','Networks','R23',3,'III-II','A',NULL,'test','BC-D'),
('23691A4014','KUDUMU GREESHMA','test','2001-01-12','Female','9676389113','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4015','G hem prasanth','test','2001-01-13','Male','9676672170','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4016','Neeli Hema prakash','test','2001-01-14','Male','9989370547','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4017','PEMMA HEMANTH KUMAR','test','2001-01-15','Male','9989394916','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4018','CHITRA HEMANTH SAI','test','2001-01-16','Male','6281158535','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4019','DEGALA JESHWANTH','test','2001-01-17','Male','9381887161','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4020','G.jithendra','test','2001-01-18','Male','8074440329','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4021','YELLRUBYLU JYOTHIKA','test','2001-01-19','Female','8498862186','Networks','R23',3,'III-II','A',NULL,'test','SC'),
('23691A4022','KURRA KARTHIK','test','2001-01-20','Male','7989775797','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4023','PUJANABOYINI KAVYA','test','2001-01-21','Female','6305999240','Networks','R23',3,'III-II','A',NULL,'test','BC-D'),
('23691A4024','AR KUSHAL RAM','test','2001-01-22','Male','6302477059','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4025','E.LIKHITHA','test','2001-01-23','Female','7981806341','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4026','KUCHI LIKITHA','test','2001-01-24','Female','8660526793','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4027','ALAM MADHURI','test','2001-01-25','Female','9347372471','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4028','RACHARLA MANJUNATH REDDY','test','2001-01-26','Male','7981856875','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4029','Pappuru manojsai','test','2001-01-27','Male','8106724022','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4030','MADHYAHNAM MOUNIKA','test','2001-01-28','Female','7382590544','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4031','Syed Mohammad Mujahid','test','2001-01-29','Male','9741884173','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4032','VIKATAKAVI  NAGAMANVITHA','test','2001-01-30','Female','7981362594','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4033','Rachepalli Nandini','test','2001-01-31','Female','9347318374','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4034','GENNE NAVYA','test','2001-02-01','Female','8919202067','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4035','N.Nikhitha sree','test','2001-02-02','Female','9394490904','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4036','PANJOORI PRATHAP REDDY','test','2001-02-03','Male','9392645425','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4037','JAMPALA PRAVALLIKA','test','2001-02-04','Female','9398638909','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4038','JALLU PRAVEEN KUMAR REDDY','test','2001-02-05','Male','9381896209','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4039','CHALLA REDDY PUSHPANJALI','test','2001-02-06','Female','8639448856','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4040','MUTHUKURU RAJESH','test','2001-02-07','Male','9989731046','Networks','R23',3,'III-II','A',NULL,'test','SC'),
('23691A4041','Singana Ravi Shankar Reddy','test','2001-02-08','Male','9100825780','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4042','GALI REDDY MOHAN','GALI CHINNA REDDEPPA','2006-10-11','Male','6302623200','Networks','R23',3,'III-II','A',NULL,'GALI KAVITHA','BC-B'),
('23691A4043','PARCHURU ROHITH','test','2001-02-10','Male','9059575735','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4044','MANCHURI SAI HARSHITHA','test','2001-02-11','Female','8309041154','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4045','VELURI SAIRAM','test','2001-02-12','Male','9494392504','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4047','CHAMANCHULA SASI KIRAN','test','2001-02-13','Male','9440543916','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4048','BODOLLA SASIDHAR REDDY','test','2001-02-14','Male','9390766361','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4049','G SATHWIK MURARI','test','2001-02-15','Male','7993356626','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4050','MOHAMMED SHAFIYA KHANAM','test','2001-02-16','Female','9515553800','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4051','SHAIK SHAGUFTHA','test','2001-02-17','Female','8688521108','Networks','R23',3,'III-II','A',NULL,'test','BC-E'),
('23691A4052','YEDAM SIVAKUMAR','test','2001-02-18','Male','8121700439','Networks','R23',3,'III-II','A',NULL,'test','SC'),
('23691A4053','EETHAMUKKALA SUKUMAR','test','2001-02-19','Male','8309797439','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4054','M SURYAVEERA','test','2001-02-20','Male','9483757825','Networks','R23',3,'III-II','A',NULL,'test','BC-B'),
('23691A4055','BOLLU SWETHA','test','2001-02-21','Female','9182880552','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4056','SYED MOHAMMED UMAIR AHMAD','test','2001-02-22','Male','9393735719','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4057','ANIGANI VANDANA','test','2001-02-23','Female','7702761562','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4058','CHATTE VARDHAN KUMAR NAIDU','test','2001-02-24','Male','9390316521','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4059','GANJIKUNTA VARSHITHA','test','2001-02-25','Female','8332099089','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4060','SUNKU VARSHITHA','test','2001-02-26','Female','6301472642','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4061','DIVAN VENKAT NIRMAL SAI','test','2001-02-27','Male','8019209614','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4062','BACHU VENKATA NAGA DHANUNJAYA GUPTA','test','2001-02-28','Male','9951674302','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4063','KALIKIRI VINEESHA','test','2005-07-04','Female','7093098331','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('23691A4064','VADDI VISHNUVARDHAN','test','2001-03-02','Male','8919893087','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('23691A4065','PASUPULETI YASHASWINI','test','2001-03-03','Female','7815962592','Networks','R23',3,'III-II','A',NULL,'test','BC-D'),
('23691A4066','R YOSHITA','test','2001-03-04','Female','8309993231','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('24695A4001','PUJARI BHANU SREE','test','2001-03-05','Female','9010621734','Networks','R23',3,'III-II','A',NULL,'test','SC'),
('24695A4002','RAGURI CHARAN','test','2001-03-06','Male','8639403880','Networks','R23',3,'III-II','A',NULL,'test','OC'),
('24695A4003','S MD SADIQ','S MD TAHER HUSSAIN','2004-08-28','Male','8985594572','Networks','R23',3,'III-II','A',NULL,'S KHADIRUNNISA','BC-E'),
('24695A4004','DERANGULA DURGA SAI','test','2001-03-08','Male','8639646499','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('24695A4005','SAKE VINODINI','test','2001-03-09','Female','7780344005','Networks','R23',3,'III-II','A',NULL,'test','BC-A'),
('24695A4006','MATLI VISHNU VARDHAN NAIDU','MATLI MURALI NAIDU','2006-07-04','Male','8106895785','Networks','R23',3,'III-II','A',NULL,'NANDALA RAJESWARI','OC');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `department` varchar(100) DEFAULT NULL,
  `regulation` varchar(10) DEFAULT NULL,
  `semester` varchar(10) DEFAULT NULL,
  `subject_code` varchar(20) DEFAULT NULL,
  `subject_name` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `subjects` VALUES
(1,'Networks','R23','III-I','23CSN107','Cryptography and Network Security'),
(2,'Networks','R23','III-I','23CSN108','Database Management Systems'),
(3,'Networks','R23','III-I','23CSN109','Network Programming'),
(4,'Networks','R23','III-I','23PHY102','Introduction to Quantum Technologies and Applications'),
(5,'Networks','R23','III-I','23CSN205','Database Management Systems Laboratory'),
(6,'Networks','R23','III-I','23CSN206','Network Programming Laboratory'),
(7,'Networks','R23','III-I','23CSN603','UI Design'),
(8,'Networks','R23','III-I','23ENG901','Technical Paper Writing and IPR'),
(9,'Networks','R23','III-I','23CSN701','Summer Internship I'),
(10,'Networks','R23','III-I','MOOC 1','Distributed Systems'),
(11,'Networks','R23','III-I','MOOC 2','PSOSC'),
(12,'Networks','R23','III-II','23CSN110','Software Engineering'),
(13,'Networks','R23','III-II','23CSN111','Internetworking with TCP/IP'),
(14,'Networks','R23','III-II','23CSN112','Cloud Computing'),
(15,'Networks','R23','III-II','23CSN401','Image Processing (Professional Elective - II)'),
(16,'Networks','R23','III-II','23CSN409','Cyber Forensics (Professional Elective - III)'),
(17,'Networks','R23','III-II','23MG3M01','E – Business (Open Elective - II)'),
(18,'Networks','R23','III-II','23MD3M01','Research Methodology (Open Elective - II)'),
(19,'Networks','R23','III-II','23CSN207','Internetworking with TCP/IP Laboratory'),
(20,'Networks','R23','III-II','23CSN208','Cloud Computing Laboratory'),
(21,'Networks','R23','III-II','23ENG601','Soft Skills'),
(22,'Networks','R23','III-II','23ECE501','Tinkering Laboratory'),
(23,'Networks','R23','III-II','23CSN801','Workshop'),
(24,'AI & ML','R23','III-II','23CSM110','Big Data Analytics'),
(25,'AI & ML','R23','III-II','23CSM111','Cloud Computing for AI'),
(26,'AI & ML','R23','III-II','23CSM112','Deep Learning'),
(27,'AI & ML','R23','III-II','23CSM405','Automata Theory and Compiler Design (Professional Elective - II)'),
(28,'AI & ML','R23','III-II','23CSM406','Reinforecement Learning (Professional Elective - III)'),
(29,'AI & ML','R23','III-II','23CSM207','Big Data and Cloud Computing Laboratory'),
(30,'AI & ML','R23','III-II','23CSM208','Deep Learning Laboratory'),
(31,'AI & ML','R23','III-II','23ECE501','Tinkering Laboratory'),
(32,'AI & ML','R23','III-II','23CSM801','Workshop'),
(33,'AI & ML','R23','III-II','23MD3M01','Research Methodology (Open Elective - II)'),
(34,'AI & ML','R23','III-II','23MG3M01','E – Business (Open Elective - II)'),
(35,'AI & ML','R23','III-II','23ENG601','Soft Skills');
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `student_backlogs`
--

DROP TABLE IF EXISTS `student_backlogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_backlogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roll_number` varchar(20) NOT NULL,
  `subject_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_student_subject` (`roll_number`,`subject_id`),
  KEY `idx_backlog_roll` (`roll_number`),
  KEY `idx_backlog_subject` (`subject_id`),
  CONSTRAINT `fk_backlog_student` FOREIGN KEY (`roll_number`) REFERENCES `students` (`roll_number`) ON DELETE CASCADE,
  CONSTRAINT `fk_backlog_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-12-14 20:47:38

DROP TABLE IF EXISTS `student_backlogs`;

CREATE TABLE `student_backlogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `roll_number` varchar(20) NOT NULL,
  `subject_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_student_subject` (`roll_number`,`subject_id`),
  KEY `idx_backlog_roll` (`roll_number`),
  KEY `idx_backlog_subject` (`subject_id`),
  CONSTRAINT `fk_backlog_student`
    FOREIGN KEY (`roll_number`) REFERENCES `students` (`roll_number`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_backlog_subject`
    FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_uca1400_ai_ci;
