from Database import reboot_database, add_tutor, add_admin, add_superuser, add_to_master_schedule, create_tables, add_discipline, update_tutoring_disciplines
reboot_database(["Computer_Science", "Mathematics", "Physics", "Economics", "Chemistry$Molecular_Biology"],'No')
create_tables(["Computer_Science", "Mathematics", "Physics", "Economics", "Chemistry$Molecular_Biology"])
add_tutor("Moises Padilla", "m_padilla@coloradocollege.edu")
add_tutor("Jessica Hannebert", "j_hannebert@coloradocollege.edu")
add_tutor("Pralad Mishra", "p_mishra@coloradocollege.edu") 
add_tutor("Giang Pham", "g_pham@coloradocollege.edu")
update_tutoring_disciplines("m_padilla@coloradocollege.edu", ["Computer_Science", "Mathematics"])
update_tutoring_disciplines("p_mishra@coloradocollege.edu", ["Computer_Science", "Chemistry$Molecular_Biology"])
update_tutoring_disciplines("g_pham@coloradocollege.edu", ["Economics", "Chemistry$Molecular_Biology"])
update_tutoring_disciplines("j_hannebert@coloradocollege.edu", ["Economics", "Physics"])
add_discipline("Computer_Science", "CS", [1, 3, 5, 7, 9, 11, 13, 15, 17, 19])
add_discipline("Mathematics", "M", [0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 17, 18, 19])
add_discipline("Physics", "P", [3, 5, 7, 9, 11, 13, 15, 17, 19])
add_discipline("Economics", "E", [1, 2, 3, 5, 7, 9, 11, 15, 19])
add_discipline("Chemistry$Molecular_Biology", "CH$MB", [0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19])
add_to_master_schedule(0, ["Computer_Science", "Mathematics", "Physics", "Economics", "Chemistry$Molecular_Biology"], ["m_padilla@coloradocollege.edu", None, None, None, None])
add_to_master_schedule(1, ["Computer_Science", "Mathematics", "Physics", "Economics", "Chemistry$Molecular_Biology"], ["p_mishra@coloradocollege.edu", None, None, None, None])

#<exit Python shell>
#python3 fill_out_schedule.py
