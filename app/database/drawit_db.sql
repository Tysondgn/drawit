
CREATE TABLE `drawing` (
  `DrawingID` int(11) NOT NULL,
  `DrafterID` varchar(20) NOT NULL,
  `DrawingLocation` varchar(500) NOT NULL,
  `Title` varchar(100) NOT NULL,
  `DrawingNumber` varchar(20) NOT NULL,
  `ClientName` varchar(100) NOT NULL,
  `ProjectLocation` varchar(500) NOT NULL,
  `ProjectCode` varchar(50) NOT NULL,
  `FeedbackAuthorityID` varchar(20) NOT NULL,
  `FeedbackStatus` varchar(20) NOT NULL,
  `ReleaseDate` datetime DEFAULT NULL,
  `RevisionAuthorityID` varchar(20) NOT NULL,
  `ReleaseRevisionStatus` varchar(20) NOT NULL,
  `Reference` varchar(500) NOT NULL,
  `BuildOfMaterial` varchar(500) NOT NULL,
  `DateCreated` datetime NOT NULL DEFAULT current_timestamp(),
  `designe_change_note` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `feedback` (
  `FeedbackID` int(11) NOT NULL,
  `DrawingID` int(11) NOT NULL,
  `DrafterID` varchar(20) NOT NULL,
  `FeedbackAuthorityID` varchar(50) NOT NULL,
  `FeedbackNote` varchar(2000) NOT NULL,
  `status` varchar(20) NOT NULL,
  `DateCreated` datetime NOT NULL DEFAULT current_timestamp(),
  `DateResponded` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `releaserevision` (
  `ReleaseRevisionID` int(11) NOT NULL,
  `RevisionAuthorityID` varchar(20) NOT NULL,
  `Title` varchar(100) NOT NULL,
  `DrawingID` int(11) NOT NULL,
  `Status` varchar(20) NOT NULL,
  `RevisionNote` varchar(1000) NOT NULL,
  `RevisionDate` datetime NOT NULL DEFAULT current_timestamp(),
  `DateCreated` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `UserID` int(11) NOT NULL,
  `DrafterID` varchar(20) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `ProfileImage` varchar(100) NOT NULL,
  `Designation` varchar(100) NOT NULL,
  `DateCreated` datetime NOT NULL DEFAULT current_timestamp(),
  `DateEdited` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`UserID`, `DrafterID`, `Name`, `Email`, `ProfileImage`, `Designation`, `DateCreated`, `DateEdited`) VALUES
(1, 'SK001', 'Harshit Kumar Sahu', 'harshitsahu.hs66@gmail.com', '', 'Chief Executive Officer', '2024-05-27 11:38:36', NULL),
(2, 'MK009', 'Iron Man', 'sidekick.webtech@gmail.com', '', 'Chief Technical Officer', '2024-05-27 11:48:09', NULL),
(3, 'sidekick001', 'krishna lodhi', 'lodhikrishna42000@gmail.com', '', 'Founder', '2024-05-28 11:16:16', NULL),
(4, '50', 'Ashutosh Rath', 'ashutoshrath012@gmail.com', '', 'CAD Engineer ', '2024-05-28 22:35:17', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `drawing`
--
ALTER TABLE `drawing`
  ADD PRIMARY KEY (`DrawingID`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`FeedbackID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`UserID`),
  ADD UNIQUE KEY `EmployeeID` (`DrafterID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `drawing`
--
ALTER TABLE `drawing`
  MODIFY `DrawingID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `FeedbackID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
