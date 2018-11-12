time xcodebuild -project AWSiOSSDKv2.xcodeproj -scheme AWSAPIGateway -configuration Release CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= CARTHAGE=YES archive  -showBuildSettings -skipUnavailableActions

customcarthage/carthage archive | tee "carthageout.txt"
frameworkfilename=$(cat carthageout.txt |  grep -o 'Created .*\.zip$'  | grep -o   '\S*\.zip$')

if [ -z  "$frameworkfilename" ];then
echo "Cannot find framework zip file from output of carthage archive"
exit 1
fi

if [ ! -f "$frameworkfilename" ]; then
echo "$frameworkfilename is not present"
exit 1
fi

mv $frameworkfilename aws-sdk-ios-carthage.framework.zip
if [ -f "aws-sdk-ios-carthage.framework.zip" ]; then
echo "$frameworkfilename is  present"
exit 0
else
    exit 1
fi
