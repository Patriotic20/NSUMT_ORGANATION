-- assign_teacher_roles.sql

-- Ensure every Teacher.user_id has the "teacher" role
DO $$
DECLARE
    v_teacher_role_id INT;
    v_user_id INT;
BEGIN
    -- 1️⃣ Check if the 'teacher' role exists in the roles table
    SELECT id INTO v_teacher_role_id FROM roles WHERE name = 'teacher';

    -- 2️⃣ If not found, create it
    IF v_teacher_role_id IS NULL THEN
        INSERT INTO roles (name)
        VALUES ('teacher')
        RETURNING id INTO v_teacher_role_id;
    END IF;

    -- 3️⃣ Loop through all user_ids from the teachers table
    FOR v_user_id IN
        SELECT user_id FROM teachers
    LOOP
        -- 4️⃣ Check if this user already has the 'teacher' role
        IF NOT EXISTS (
            SELECT 1
            FROM user_roles
            WHERE user_id = v_user_id
              AND role_id = v_teacher_role_id
        ) THEN
            -- 5️⃣ If not, insert into user_roles
            INSERT INTO user_roles (user_id, role_id)
            VALUES (v_user_id, v_teacher_role_id);
        END IF;
    END LOOP;

    RAISE NOTICE '✅ Teacher role ensured and assigned where missing.';
END $$;
