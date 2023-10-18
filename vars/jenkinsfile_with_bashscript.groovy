def call(){
    def podTemplate = "podTemplate.yaml"
    def prScript = libraryResource "pr.sh"
    

    pipeline {
        agent {
            kubernetes {
                label "jenkins-${UUID.randomUUID().toString()}"
                yamlFile "$podTemplate"
            }
        }
        environment {
            NAME = "${jobNameParts[0]}"
            VERSION = "${env.GIT_COMMIT}-${env.BUILD_ID}"
            IMAGE_REPO = "sarthaksatish"
            GITHUB_TOKEN = credentials('githubpat')
            NAMESPACE = "jenkins"
            HELM_CHART_DIRECTORY = "charts/priyankalearnings"
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
                            sh "gradle clean build"
                        }
                    }
                }
            }


            stage('Build Image') {
                steps {
                    script {
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
                        writeFile file: "pr.sh", text: prScript
                        sh "bash pr.sh"
                    }
                }
            } 
        }
    }
}