git clone https://github.com/awslabs/aws-sdk-ios-samples.git ios-sample-2
cfolder=$(pwd)
cd ios-sample-2/
git checkout deviceFarm
cd S3TransferUtility-Sample/Swift/
cp $cfolder/awsconfiguration.json S3BackgroundTransferSampleSwift/awsconfiguration.json
pod install
xcodebuild -workspace S3TransferUtilitySampleSwift.xcworkspace -scheme "S3TransferUtilitySampleSwiftUITests" -destination 'platform=iOS Simulator,name=iPhone 8 Plus,OS=11.2' test
cd $cfolder

