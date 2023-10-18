def call(){

    def podTemplate = libraryResource('podTemplate.yaml')
    def createPrAndAddLabelsScript = libraryResource "CreatePrAndAddLabels.py"
    def requirementsTxt = libraryResource "requirements.txt"
    def dockerfile = libraryResource "Dockerfile"

    pipeline {
        agent {
            kubernetes {
                inheritFrom 'jenkins-${UUID.randomUUID().toString()}'
                yaml "$podTemplate"
            }
        }
        environment {
            NAME = "${env.NAME}"
            VERSION = "${env.GIT_COMMIT}-${env.BUILD_ID}"
            IMAGE_REPO = "sarthaksatish"
            GITHUB_TOKEN = credentials('githubpat')
        }
        stages {
            stage('Unit Tests') {
                    steps {
                    echo 'Implement unit tests if applicable.'
                    echo 'This stage is a sample placeholder'
                }
            }
            
            stage('Gradle build') {
                steps {
                    script {
                        container(name: 'gradle') {
                            sh "gradle clean build -x test"
                        }
                    }
                }
            }

            stage('Build Image') {
                steps {
                    script {
                        writeFile file: "Dockerfile", text: dockerfile
                        container('kaniko') {
                            sh '''
                            /kaniko/executor --build-arg NAME=${NAME} --context `pwd` --destination ${IMAGE_REPO}/${NAME}:${VERSION}
                            '''
                        }
                    }
                }
            }
            
            stage('Clone/Pull Repo') {
                steps {
                    script {
                        if (fileExists('helm-charts')) {
                            echo 'Cloned repo already exists - Pulling latest changes'
                            dir("helm-charts") {
                                sh 'git pull'
                            }
                        } else {
                            sh 'git clone https://github.com/sarsatis/helm-charts'
                            sh 'ls -ltr'
                        }
                    }
                }
            }

            stage('Commit & Push') {
                steps {
                    script {
                        dir("helm-charts/manifests/${NAME}/sit/immutable") {
                            withCredentials([usernamePassword(
                                credentialsId: 'githubpat',
                                usernameVariable: 'username',
                                passwordVariable: 'password'
                            )]) {
                                encodedPassword = URLEncoder.encode("$password", 'UTF-8')
                                echo "sa ${encodedPassword}"
                                sh "git config --global user.email 'jenkins@ci.com'"
                                sh "git remote set-url origin https://${username}:${encodedPassword}@github.com/${username}/helm-charts.git"
                                sh 'sed -i "s#tag:.*#tag: ${VERSION}#g" values.yaml'
                                sh "git checkout -b ${NAME}-${env.BUILD_ID}"
                                sh 'cat values.yaml'
                                sh 'git add values.yaml'
                                sh 'git commit -am "Updated image version for Build - $VERSION"'
                                echo 'push started'
                                sh "git push origin ${NAME}-${env.BUILD_ID}"
                            }
                            echo 'push complete'
                        }
                    }
                }
            }

            stage('Raise PR') {
                steps {
                    script {
                        writeFile file: "CreatePrAndAddLabel.py", text: createPrAndAddLabelsScript
                        writeFile file: "requirements.txt", text: requirementsTxt
                        container(name: 'python') {
                            sh '''
                                printenv
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