def call(){

    def podTemplate = libraryResource('podTemplate.yaml')
    def createPrAndAddLabelsScript = libraryResource "CreatePrAndAddLabelsWithOop.py"
    def requirementsTxt = libraryResource "RequirementsWithOop.txt"
    def dockerfile = libraryResource "DockerfileJava"
    def jobNameParts = env.JOB_NAME.split('/')

    pipeline {
        agent {
            kubernetes {
                inheritFrom 'jenkins-${UUID.randomUUID().toString()}'
                yaml "$podTemplate"
            }
        }
        environment {
            NAME = "${jobNameParts[0]}"
            VERSION = "${env.GIT_COMMIT}-${env.BUILD_ID}"
            IMAGE_REPO = "sarthaksatish"
            GITHUB_TOKEN = credentials('githubpat')
        }
        stages {
            stage('Unit Tests') {
                steps {
                    sh "printenv"
                    echo 'Implement unit tests if applicable.'
                    echo 'This stage is a sample placeholder'
                }
            }
            
            // stage('Gradle build') {
            //     steps {
            //         script {
            //             container(name: 'gradle') {
            //                 sh "gradle clean build -x test"
            //             }
            //         }
            //     }
            // }

            // stage('Build Image') {
            //     steps {
            //         script {
            //             writeFile file: "Dockerfile", text: dockerfile
            //             container('kaniko') {
            //                 sh '''
            //                 /kaniko/executor --build-arg NAME=${NAME} --context `pwd` --destination ${IMAGE_REPO}/${NAME}:${VERSION}
            //                 '''
            //             }
            //         }
            //     }
            // }

            stage('Raise PR') {
                steps {
                    script {
                        writeFile file: "CreatePrAndAddLabel.py", text: createPrAndAddLabelsScript
                        writeFile file: "requirements.txt", text: requirementsTxt
                        container(name: 'python') {
                            sh '''
                                pip3 install -r requirements.txt
                                python3 CreatePrAndAddLabel.py
                            '''
                        }
                    }
                }
            }
        }
    }
}