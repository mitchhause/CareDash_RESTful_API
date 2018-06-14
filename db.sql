--create tables for database
CREATE TABLE doctor(id SERIAL NOT NULL,
                     name VARCHAR(255),
                     PRIMARY KEY(id)
                    );

CREATE TABLE review(id SERIAL NOT NULL,
                    doctor_id INT NOT NULL,
                    description VARCHAR(255),
                    PRIMARY KEY(id),
                    FOREIGN KEY (doctor_id) REFERENCES Doctor(id) ON DELETE CASCADE
                   );
