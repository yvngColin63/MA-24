import pygame
import sys

# INTERFACE GRAPHIQUE
# On définit la taille de notre damier
lignes = 10
colonnes = 10
taille_case = 60

# Calcul automatique de la taille de la fenêtre
largeur_fenetre = colonnes * taille_case
hauteur_fenetre = lignes * taille_case

# Nos deux couleurs pour le damier (comme un vrai jeu de dames !)
couleur_claire = (240, 240, 240)  # Presque blanc
couleur_foncee = (60, 60, 60)  # Gris foncé


def dessiner_damier(ecran):
    """
    Cette fonction dessine toutes les cases du damier.
    Elle alterne entre clair et foncé, comme un échiquier.
    """
    # On parcourt chaque ligne
    for ligne in range(lignes):
        # Puis chaque colonne
        for colonne in range(colonnes):
            # Astuce : si la somme ligne+colonne est paire, on met du clair
            # sinon on met du foncé. Ça crée l'effet damier !
            if (ligne + colonne) % 2 == 0:
                couleur = couleur_claire
            else:
                couleur = couleur_foncee

            # On dessine un rectangle pour cette case
            x = colonne * taille_case
            y = ligne * taille_case
            pygame.draw.rect(ecran, couleur, (x, y, taille_case, taille_case))


# Le programme principal commence ici
pygame.init()
ecran = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
pygame.display.set_caption("Mon damier 10x10")

# Boucle principale - le cœur du jeu qui tourne en continu
en_cours = True
while en_cours:
    # On vérifie si le joueur veut fermer la fenêtre
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False

    # On dessine notre beau damier
    dessiner_damier(ecran)

    # On actualise l'affichage pour voir les changements
    pygame.display.flip()

# Quand on sort de la boucle, on ferme proprement
pygame.quit()
sys.exit()