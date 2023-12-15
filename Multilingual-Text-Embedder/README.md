## Future Improvements
- 효율적인 재학습
    - 데이터 양 많음(약 130M)
    - loss → nan 문제로 전체 데이터의 13% 정도밖에 학습하지 못함
        - loss 소멸을 방지하면서 전체 데이터를 학습시킬 수 있는 적절한 learning strategy 필요
    - GPU의 한계로 커다란 모델 학습 시키지 못함
        - LoRA 방식을 썼음에도 데이터의 양이 매우 방대함
        - large 모델(1024차원) 학습 가능성
