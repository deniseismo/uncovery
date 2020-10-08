export class Wave {
  constructor(method) {
    this.method = method;
    this.shapes = [
      "M0,320L6.2,293.3C12.3,267,25,213,37,208C49.2,203,62,245,74,250.7C86.2,256,98,224,111,213.3C123.1,203,135,213,148,218.7C160,224,172,224,185,186.7C196.9,149,209,75,222,58.7C233.8,43,246,85,258,112C270.8,139,283,149,295,165.3C307.7,181,320,203,332,186.7C344.6,171,357,117,369,106.7C381.5,96,394,128,406,160C418.5,192,431,224,443,234.7C455.4,245,468,235,480,213.3C492.3,192,505,160,517,165.3C529.2,171,542,213,554,218.7C566.2,224,578,192,591,181.3C603.1,171,615,181,628,202.7C640,224,652,256,665,234.7C676.9,213,689,139,702,138.7C713.8,139,726,213,738,245.3C750.8,277,763,267,775,224C787.7,181,800,107,812,80C824.6,53,837,75,849,69.3C861.5,64,874,32,886,16C898.5,0,911,0,923,21.3C935.4,43,948,85,960,117.3C972.3,149,985,171,997,186.7C1009.2,203,1022,213,1034,208C1046.2,203,1058,181,1071,192C1083.1,203,1095,245,1108,256C1120,267,1132,245,1145,202.7C1156.9,160,1169,96,1182,101.3C1193.8,107,1206,181,1218,181.3C1230.8,181,1243,107,1255,69.3C1267.7,32,1280,32,1292,64C1304.6,96,1317,160,1329,160C1341.5,160,1354,96,1366,74.7C1378.5,53,1391,75,1403,117.3C1415.4,160,1428,224,1434,256L1440,288L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z",
      "M0,96L6.2,122.7C12.3,149,25,203,37,208C49.2,213,62,171,74,170.7C86.2,171,98,213,111,224C123.1,235,135,213,148,208C160,203,172,213,185,224C196.9,235,209,245,222,213.3C233.8,181,246,107,258,101.3C270.8,96,283,160,295,181.3C307.7,203,320,181,332,144C344.6,107,357,53,369,53.3C381.5,53,394,107,406,138.7C418.5,171,431,181,443,197.3C455.4,213,468,235,480,240C492.3,245,505,235,517,229.3C529.2,224,542,224,554,218.7C566.2,213,578,203,591,176C603.1,149,615,107,628,96C640,85,652,107,665,117.3C676.9,128,689,128,702,160C713.8,192,726,256,738,261.3C750.8,267,763,213,775,202.7C787.7,192,800,224,812,213.3C824.6,203,837,149,849,117.3C861.5,85,874,75,886,64C898.5,53,911,43,923,74.7C935.4,107,948,181,960,213.3C972.3,245,985,235,997,208C1009.2,181,1022,139,1034,112C1046.2,85,1058,75,1071,69.3C1083.1,64,1095,64,1108,96C1120,128,1132,192,1145,202.7C1156.9,213,1169,171,1182,176C1193.8,181,1206,235,1218,234.7C1230.8,235,1243,181,1255,160C1267.7,139,1280,149,1292,138.7C1304.6,128,1317,96,1329,69.3C1341.5,43,1354,21,1366,21.3C1378.5,21,1391,43,1403,42.7C1415.4,43,1428,21,1434,10.7L1440,0L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z",
      "M0,160L6.2,176C12.3,192,25,224,37,240C49.2,256,62,256,74,240C86.2,224,98,192,111,181.3C123.1,171,135,181,148,192C160,203,172,213,185,229.3C196.9,245,209,267,222,266.7C233.8,267,246,245,258,224C270.8,203,283,181,295,176C307.7,171,320,181,332,170.7C344.6,160,357,128,369,128C381.5,128,394,160,406,192C418.5,224,431,256,443,234.7C455.4,213,468,139,480,101.3C492.3,64,505,64,517,90.7C529.2,117,542,171,554,213.3C566.2,256,578,288,591,288C603.1,288,615,256,628,250.7C640,245,652,267,665,234.7C676.9,203,689,117,702,80C713.8,43,726,53,738,85.3C750.8,117,763,171,775,186.7C787.7,203,800,181,812,160C824.6,139,837,117,849,106.7C861.5,96,874,96,886,90.7C898.5,85,911,75,923,64C935.4,53,948,43,960,42.7C972.3,43,985,53,997,90.7C1009.2,128,1022,192,1034,224C1046.2,256,1058,256,1071,245.3C1083.1,235,1095,213,1108,213.3C1120,213,1132,235,1145,250.7C1156.9,267,1169,277,1182,245.3C1193.8,213,1206,139,1218,122.7C1230.8,107,1243,149,1255,154.7C1267.7,160,1280,128,1292,101.3C1304.6,75,1317,53,1329,53.3C1341.5,53,1354,75,1366,101.3C1378.5,128,1391,160,1403,176C1415.4,192,1428,192,1434,192L1440,192L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z",
      "M0,160L6.2,149.3C12.3,139,25,117,37,96C49.2,75,62,53,74,58.7C86.2,64,98,96,111,138.7C123.1,181,135,235,148,256C160,277,172,267,185,266.7C196.9,267,209,277,222,261.3C233.8,245,246,203,258,154.7C270.8,107,283,53,295,42.7C307.7,32,320,64,332,112C344.6,160,357,224,369,240C381.5,256,394,224,406,197.3C418.5,171,431,149,443,128C455.4,107,468,85,480,96C492.3,107,505,149,517,144C529.2,139,542,85,554,69.3C566.2,53,578,75,591,117.3C603.1,160,615,224,628,234.7C640,245,652,203,665,197.3C676.9,192,689,224,702,202.7C713.8,181,726,107,738,96C750.8,85,763,139,775,160C787.7,181,800,171,812,160C824.6,149,837,139,849,160C861.5,181,874,235,886,245.3C898.5,256,911,224,923,213.3C935.4,203,948,213,960,208C972.3,203,985,181,997,149.3C1009.2,117,1022,75,1034,48C1046.2,21,1058,11,1071,53.3C1083.1,96,1095,192,1108,202.7C1120,213,1132,139,1145,117.3C1156.9,96,1169,128,1182,149.3C1193.8,171,1206,181,1218,165.3C1230.8,149,1243,107,1255,80C1267.7,53,1280,43,1292,74.7C1304.6,107,1317,181,1329,208C1341.5,235,1354,213,1366,218.7C1378.5,224,1391,256,1403,261.3C1415.4,267,1428,245,1434,234.7L1440,224L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z",
      "M0,288L6.2,277.3C12.3,267,25,245,37,224C49.2,203,62,181,74,186.7C86.2,192,98,224,111,213.3C123.1,203,135,149,148,117.3C160,85,172,75,185,85.3C196.9,96,209,128,222,138.7C233.8,149,246,139,258,122.7C270.8,107,283,85,295,101.3C307.7,117,320,171,332,208C344.6,245,357,267,369,282.7C381.5,299,394,309,406,293.3C418.5,277,431,235,443,208C455.4,181,468,171,480,181.3C492.3,192,505,224,517,229.3C529.2,235,542,213,554,202.7C566.2,192,578,192,591,181.3C603.1,171,615,149,628,138.7C640,128,652,128,665,122.7C676.9,117,689,107,702,128C713.8,149,726,203,738,229.3C750.8,256,763,256,775,224C787.7,192,800,128,812,101.3C824.6,75,837,85,849,96C861.5,107,874,117,886,133.3C898.5,149,911,171,923,186.7C935.4,203,948,213,960,208C972.3,203,985,181,997,165.3C1009.2,149,1022,139,1034,138.7C1046.2,139,1058,149,1071,138.7C1083.1,128,1095,96,1108,80C1120,64,1132,64,1145,74.7C1156.9,85,1169,107,1182,128C1193.8,149,1206,171,1218,192C1230.8,213,1243,235,1255,218.7C1267.7,203,1280,149,1292,117.3C1304.6,85,1317,75,1329,64C1341.5,53,1354,43,1366,64C1378.5,85,1391,139,1403,144C1415.4,149,1428,107,1434,85.3L1440,64L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z",
      "M0,160L6.2,170.7C12.3,181,25,203,37,186.7C49.2,171,62,117,74,128C86.2,139,98,213,111,240C123.1,267,135,245,148,202.7C160,160,172,96,185,58.7C196.9,21,209,11,222,32C233.8,53,246,107,258,112C270.8,117,283,75,295,69.3C307.7,64,320,96,332,117.3C344.6,139,357,149,369,144C381.5,139,394,117,406,112C418.5,107,431,117,443,117.3C455.4,117,468,107,480,106.7C492.3,107,505,117,517,117.3C529.2,117,542,107,554,85.3C566.2,64,578,32,591,53.3C603.1,75,615,149,628,202.7C640,256,652,288,665,304C676.9,320,689,320,702,293.3C713.8,267,726,213,738,197.3C750.8,181,763,203,775,202.7C787.7,203,800,181,812,149.3C824.6,117,837,75,849,64C861.5,53,874,75,886,106.7C898.5,139,911,181,923,192C935.4,203,948,181,960,192C972.3,203,985,245,997,245.3C1009.2,245,1022,203,1034,202.7C1046.2,203,1058,245,1071,240C1083.1,235,1095,181,1108,154.7C1120,128,1132,128,1145,128C1156.9,128,1169,128,1182,117.3C1193.8,107,1206,85,1218,69.3C1230.8,53,1243,43,1255,74.7C1267.7,107,1280,181,1292,192C1304.6,203,1317,149,1329,149.3C1341.5,149,1354,203,1366,202.7C1378.5,203,1391,149,1403,138.7C1415.4,128,1428,160,1434,176L1440,192L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z",
      "M0,64L6.2,58.7C12.3,53,25,43,37,42.7C49.2,43,62,53,74,90.7C86.2,128,98,192,111,197.3C123.1,203,135,149,148,144C160,139,172,181,185,181.3C196.9,181,209,139,222,128C233.8,117,246,139,258,149.3C270.8,160,283,160,295,186.7C307.7,213,320,267,332,250.7C344.6,235,357,149,369,117.3C381.5,85,394,107,406,122.7C418.5,139,431,149,443,160C455.4,171,468,181,480,202.7C492.3,224,505,256,517,224C529.2,192,542,96,554,96C566.2,96,578,192,591,229.3C603.1,267,615,245,628,240C640,235,652,245,665,240C676.9,235,689,213,702,208C713.8,203,726,213,738,229.3C750.8,245,763,267,775,240C787.7,213,800,139,812,112C824.6,85,837,107,849,149.3C861.5,192,874,256,886,240C898.5,224,911,128,923,74.7C935.4,21,948,11,960,16C972.3,21,985,43,997,69.3C1009.2,96,1022,128,1034,133.3C1046.2,139,1058,117,1071,128C1083.1,139,1095,181,1108,218.7C1120,256,1132,288,1145,288C1156.9,288,1169,256,1182,213.3C1193.8,171,1206,117,1218,80C1230.8,43,1243,21,1255,16C1267.7,11,1280,21,1292,58.7C1304.6,96,1317,160,1329,165.3C1341.5,171,1354,117,1366,96C1378.5,75,1391,85,1403,128C1415.4,171,1428,245,1434,282.7L1440,320L1440,320L1433.8,320C1427.7,320,1415,320,1403,320C1390.8,320,1378,320,1366,320C1353.8,320,1342,320,1329,320C1316.9,320,1305,320,1292,320C1280,320,1268,320,1255,320C1243.1,320,1231,320,1218,320C1206.2,320,1194,320,1182,320C1169.2,320,1157,320,1145,320C1132.3,320,1120,320,1108,320C1095.4,320,1083,320,1071,320C1058.5,320,1046,320,1034,320C1021.5,320,1009,320,997,320C984.6,320,972,320,960,320C947.7,320,935,320,923,320C910.8,320,898,320,886,320C873.8,320,862,320,849,320C836.9,320,825,320,812,320C800,320,788,320,775,320C763.1,320,751,320,738,320C726.2,320,714,320,702,320C689.2,320,677,320,665,320C652.3,320,640,320,628,320C615.4,320,603,320,591,320C578.5,320,566,320,554,320C541.5,320,529,320,517,320C504.6,320,492,320,480,320C467.7,320,455,320,443,320C430.8,320,418,320,406,320C393.8,320,382,320,369,320C356.9,320,345,320,332,320C320,320,308,320,295,320C283.1,320,271,320,258,320C246.2,320,234,320,222,320C209.2,320,197,320,185,320C172.3,320,160,320,148,320C135.4,320,123,320,111,320C98.5,320,86,320,74,320C61.5,320,49,320,37,320C24.6,320,12,320,6,320L0,320Z"
    ]
    this.params = {
      "by_spotify": {
        "d": this.shapes[Math.floor(Math.random() * this.shapes.length)],
        "fill": "#1DB954"
      },
      "by_username": {
        "d": this.shapes[Math.floor(Math.random() * this.shapes.length)],
        "fill": "#d51007"
      },
      "by_artist": {
        "d": this.shapes[Math.floor(Math.random() * this.shapes.length)],
        "fill": "#FFDB57"
      },
      "explore": {
        "d": this.shapes[Math.floor(Math.random() * this.shapes.length)],
        "fill": "#000"
      }
    }
  }
  getWave() {
    return this.params[this.method]
  }
}