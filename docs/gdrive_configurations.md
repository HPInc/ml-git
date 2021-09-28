# Google Drive API configuration

This section aims to explain how to enable Google Drive API and configure OAuth 2.0 credentials to use with ML-Git.

#### Enabling Drive API

You need to create a project in Google developer console to activate Drive API, follow instructions bellow:

**1. Access [console developer](https://console.developers.google.com/) and click on create project:**

![create_project](drive_api_pic/start_screen.png)

**2. Then type name of your preference and click on "CREATE" button:**

![project_name](drive_api_pic/create_project_screen.png)

**3. Go back to dashboard and enable Drive API:**


![enable_api](drive_api_pic/enable_api.png)

**4. Search for Drive API on search bar:**

![search_bar](drive_api_pic/search_api_bar.png)

![search_bar](drive_api_pic/enable_api_buttom.png)

#### Creating credentials

When you finish Enabling API step, you need to create your credentials and configure authentication consent screen.

**1. Click on create credentials:**

![select_credentials_type](drive_api_pic/select_credentials_api.png)

![cosent_screen](drive_api_pic/consent_screen.png)


**2. Select user type of your consent:**

![consent_user_type](drive_api_pic/consent_user_type.png)

**3. Add application name to authentication consent screen:**

![app_name_consent](drive_api_pic/consent_app_name.png)

**4. Change application's scope if you prefer and save:**

![consent_save](drive_api_pic/consent_save.png)

**5. Go back to dashboard and click on create credentials and generate your API KEY:**

![create_credentials](drive_api_pic/create_credentials_screen.png)

![api_key](drive_api_pic/create_api_key.png)

**6. Generate OAuth client id:**

![oauth_client_id](drive_api_pic/create_oauth_client_id.png)

**7. Add client name and select application type:**

![select_app_type](drive_api_pic/select_other_oauth_client.png)

**8. Finally you can download your credentials file:**

![dash_board_download_credentials.json](drive_api_pic/download_credentials_json.png)

# Setting up a ML-Git project with Google Drive #

Create directory with name  of your preference and copy your credentials  file with name **credentials.json** inside the directory.

Add storage configurations example:

```
ml-git repository storage add path-in-your-drive --type=gdriveh --credentials=/home/profile/.gdrive
```

After that initialize the metadata repository:

```
ml-git datasets init
```



We strongly recommend that you add `push_threads_count: 10` option in your .**ml-git/config.yaml**, because of Google Drive API request limit of 10/s. This option change the number of workers used in multithreading push process, by default the number of workers is cpu numbers multiplied by 5. 

The push command was tested with 10 workers and the request limit was not exceeded.

Configuration example:

```
batch_size: 20
push_threads_count: 10
datasets:
  git: ''
labels:
  git: ''
models:
  git: ''
storages:
  s3:
    mlgit-datasets:
      aws-credentials:
        profile: default
      region: us-east-1
```

