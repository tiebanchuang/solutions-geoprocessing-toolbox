# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2015 - 2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 TestRunner.py
------------------------------------------------------------------------------
 requirements:
 * ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
 * Python 2.7 or Python 3.4
 author: ArcGIS Solutions
 company: Esri
==================================================
 description:
 This test suite collects all of the capability toolbox test suites:
 * HelicopterLandingZoneToolsTestSuite.py
 * ERGToolsTestSuite.py
 * PointOfOriginToolsTestSuite.py

==================================================
 history:
 10/06/2015 - MF - placeholder
 10/30/2015 - MF - tests running
 17/25/2017 - MF - remove deprecated tool tests
==================================================
'''

import datetime
import logging
import os
import sys
import unittest

import arcpy

import Configuration
import UnitTestUtilities
import DataDownload

logFileFromBAT = None
if len(sys.argv) > 1:
    logFileFromBAT = sys.argv[1] #if we have an explicit log file name passed in

def main():
    ''' main test logic '''
    print("TestRunner.py - main")

    if Configuration.DEBUG == True:
        print("Debug messaging is ON")
        logLevel = logging.DEBUG
    else:
        print("Debug messaging is OFF")
        logLevel = logging.INFO

    # setup logger
    if not logFileFromBAT == None:
        Configuration.Logger = UnitTestUtilities.initializeLogger(logFileFromBAT, logLevel)
    else:
        Configuration.GetLogger(logLevel)

    print("Logging results to: " + str(Configuration.LoggerFile))
    UnitTestUtilities.setUpLogFileHeader()

    result = runTestSuite()

    logTestResults(result)

    return result.wasSuccessful()

def logTestResults(result):
    ''' Write the log file '''
    resultHead = resultsHeader(result)
    Configuration.Logger.info(resultHead)

    errorLogLines = getErrorResultsAsList(result)
    for errorLogLine in errorLogLines :
        # strip unicode chars so they don't mess up print/log file
        line = errorLogLine.encode('ascii','ignore').decode('ascii')
        Configuration.Logger.error(line)

    endOfTestMsg = "END OF TEST ========================================="
    Configuration.Logger.info(endOfTestMsg)

    return

def resultsHeader(result):

    if result is None:
        return

    ''' Generic header for the results in the log file '''
    errorCount   = len(result.errors)
    failureCount = len(result.failures)
    skippedCount = len(result.skipped)
    nonPassedCount = errorCount + failureCount + skippedCount

    passedCount  = result.testsRun - nonPassedCount
    # testsRun should be > 0 , but just in case
    percentPassed = ((passedCount / result.testsRun) * 100.0) if (result.testsRun > 0) else 0.0

    msg = "\nRESULTS =================================================\n"
    msg += "Number of tests run: " + str(result.testsRun) + "\n"
    msg += "Number succeeded: " + str(passedCount) + "\n"
    msg += "Number of errors: " + str(errorCount) + "\n"
    msg += "Number of failures: " + str(failureCount) + "\n"
    msg += "Number of tests skipped: " + str(skippedCount) + "\n"
    msg += "Percent passing: %3.1f" % (percentPassed) + "\n"
    msg += "=========================================================\n"
    return msg

def getErrorResultsAsList(result):
    results = []
    if len(result.errors) > 0:
        results.append("ERRORS ==================================================")
        for test in result.errors:
            for error in test:
                strError = str(error)
                # For errors containing newlines, break these up so they are more readable
                results += strError.strip().splitlines()

    if len(result.failures) > 0:
        results.append("FAILURES ================================================")
        for test in result.failures:
            for failure in test:
                strFailure = str(failure)
                results += strFailure.strip().splitlines()

    return results

def runTestSuite():
    ''' collect all test suites before running them '''
    if Configuration.DEBUG == True: print("TestRunner.py - runTestSuite")
    testSuite = unittest.TestSuite()
    result = unittest.TestResult()

    #What Platform are we running on?
    Configuration.GetPlatform()
    Configuration.Logger.info('Running on Platform: ' + Configuration.Platform)

    testSuite.addTests(addClearingOperationsSuite())
    testSuite.addTests(addGeoNamesSuite())
    testSuite.addTests(addIncidentAnalysisSuite())
    testSuite.addTests(addMilitaryFeaturesSuite())
    testSuite.addTests(addSunPositionAnalysisSuite())

    # This suite(DistanceToAssets) must be run manually 
    # - because it requires you to first logon to AGSOnline:
    # testSuite.addTests(addDistanceToAssetsSuite())

    #TODO: MAoT Test Suite
    #TODO: MAoW Test Suite

    Configuration.Logger.info("running " + str(testSuite.countTestCases()) + " tests...")

    # Run all of the tests added above
    testSuite.run(result)

    Configuration.Logger.info("Test success: {0}".format(str(result.wasSuccessful())))

    return result

def addClearingOperationsSuite():
    '''Add all Clearing operations Tests'''
    Configuration.Logger.debug("TestRunner.py - addClearingOperationsSuite")
    from clearing_operations_tests import ClearingOperationsTestSuite
    suite = ClearingOperationsTestSuite.getTestSuite()
    return suite

def addIncidentAnalysisSuite():
    ''' Add all IncidentAnalysis tests  '''
    Configuration.Logger.debug("TestRunner.py - addIncidentAnalysisSuite")
    from incident_analysis_tests import IncidentAnalysisToolsTestSuite
    suite = IncidentAnalysisToolsTestSuite.getTestSuite()
    return suite

def addSunPositionAnalysisSuite():
    ''' Add all SunPositionAnalysis tests '''
    Configuration.Logger.debug("TestRunner.py - addSunPositionAnalysisSuite")
    from sun_position_analysis_tests import SunPositionAnalysisToolsTestSuite
    suite = SunPositionAnalysisToolsTestSuite.getTestSuite()
    return suite

def addGeoNamesSuite():
    ''' Add all GeoNames tests '''
    Configuration.Logger.debug("TestRunner.py - addGeoNamesSuite")
    from geonames_tests import GeoNamesToolsTestSuite
    suite = GeoNamesToolsTestSuite.getTestSuite()
    return suite

def addDistanceToAssetsSuite():
    ''' Add all DistanceToAssets tests '''
    Configuration.Logger.debug("TestRunner.py - addDistanceToAssetsSuite")
    from distance_to_assets_tests import DistanceToAssetsTestSuite
    suite = DistanceToAssetsTestSuite.getTestSuite()
    return suite
    
def addMilitaryFeaturesSuite():
    ''' Add all MilitaryFeatures tests '''
    Configuration.Logger.debug("TestRunner.py - addMilitaryFeaturesSuite")
    from military_features_tests import MilitaryFeaturesToolsTestSuite
    suite = MilitaryFeaturesToolsTestSuite.getTestSuite()
    return suite

# MAIN =============================================
if __name__ == "__main__":
    if Configuration.DEBUG == True:
        print("Starting TestRunner.py")

    exitAsBoolean = main()

    exitAsCode = 0 if exitAsBoolean else 1

    sys.exit(exitAsCode)
