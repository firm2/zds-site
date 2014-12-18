# language: fr
Feature: Inscription
    Pour parvenir à utiliser le site pleinement
    En tant qu'utilisateur nous devons être inscrit

    Scenario: Acceder à la page d'incsription étant déconnecté
        Je ne suis pas connecté
        Alors Je vais sur le lien inversé "register"
        Alors Je suis sur le template "member/register/index.html"
        Alors Je vois dans le titre1 "Inscription"

    Scenario: Réaliser une ou plusieurs inscription(s)
        Utiliser selenium
        Je ne suis pas connecté
        Supposons un timeout de "10000" sec
        Et Je vais sur le lien inversé "register"
        Je vois que les champs obligatoires du formulaire "RegisterForm" sont présents
        Je remplis le champ "id_email" avec "<email>"
        Je remplis le champ "id_password1" avec "<password1>"
        Je remplis le champ "id_password_confirm" avec "<password2>"
        Je remplis le champ "id_username" avec "<username>"
        Clique sur le bouton "input[name=submit]"
        Le résultat de la soumission du formulaire doit être "<result>"
        Ne plus utiliser selenium

    Examples:
        | email                    | password1   | password2   | username | result |
        | testing<<rnd>>@gmail.com | Testings123 | Testings123 | Testings | pass   |
        | testing<<rnd>>@gmail.com | Testings123 | Testings123 | Testings | fail   |
        | testing<<rnd>>@gmail.com | Testings123 |  estings123 | Testings | fail   |
        | testing<<rnd>>@gmail.com | Testings123 | Testings123 | Testings | fail   |
        | testing<<rnd>>@gmail.com | Testings123 | Testings123 | Testings | pass   |
