import cv2
from cvzone.HandTrackingModule import HandDetector
import boto3

allOS=[]
ec2=boto3.resource('ec2')
elb= boto3.client('elb')

response=elb.create_load_balancer(
    LoadBalancerName='MadeByBoto3',
    Listeners=[
        {
            'Protocol': 'HTTP',
            'LoadBalancerPort': 80,
            'InstanceProtocol': 'HTTP',
            'InstancePort': 80
        },
    ],
    AvailabilityZones=[
        "ap-south-1a",
        "ap-south-1b",
        "ap-south-1c"
    ]
)
cap = cv2.VideoCapture(1)
detector = HandDetector(maxHands=1 , detectionCon=0.8 )

def genOS():
    instances= ec2.create_instances(MinCount=1, MaxCount=1, InstanceType="t2.micro", ImageId="ami-0a2acf24c0d86e927", SecurityGroupIds=['sg-0e1df919b8da67f2e'])
    elb.register_instances_with_load_balancer(
        LoadBalancerName='MadeByBoto3',
        Instances=[
            {
                'InstanceId': instances[0].id
            }
        ]
    )
    return instances[0].id
    
def delOS(id):
    elb.deregister_instances_from_load_balancer(
        LoadBalancerName='MadeByBoto3',
        Instances=[
            {
                'InstanceId': id
            },
        ]
    )
    ec2.instances.filter(InstanceIds=[id]).terminate()
    
while True:
    ret,  photo = cap.read()
    hand = detector.findHands(photo)
    if hand:
        detectHand = hand[0]
        if detectHand:
            fingerup = detector.fingersUp(detectHand[0])
            if detectHand[0]['type'] == 'Left':
                for i in fingerup:
                    if i==1:
                        allOS.append(genOS())
            elif detectHand[0]['type'] == 'Right':
                for i in fingerup:
                    if i==1 and allOS != []:
                        delOS(allOS.pop())
                            
                        
    cv2.imshow("my photo", photo)
    if cv2.waitKey(1) == 27:
        break
        
cv2.destroyAllWindows()
cap.release()
